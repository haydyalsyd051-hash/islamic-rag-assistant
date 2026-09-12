"""توليد الإجابة النهائية بالاعتماد فقط على السياق المسترجَع (RAG).

بيدعم مزوّدين، يتم الاختيار بينهم عبر GENERATION_PROVIDER في .env:
- "ollama"    : نموذج محلي عبر Ollama (مجاني، offline، جودة أقل من Claude)
- "anthropic" : Claude API (جودة أعلى، يحتاج مفتاح API ومصاريف حسب الاستخدام)
"""

import logging
from typing import Any

import httpx

try:
    from anthropic import Anthropic, APIError  # pyright: ignore[reportMissingImports]
except ImportError:  # pragma: no cover - dependency is optional for local Ollama usage
    Anthropic = None  # type: ignore[assignment]

    class APIError(Exception):
        """Fallback APIError used when the optional anthropic package is unavailable."""

from app.core.config import Settings

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are an Islamic Seerah RAG assistant.

Your task is to answer the user's question using ONLY the retrieved context.

Strict rules:
1. Use ONLY the information explicitly stated in the context.
2. Do NOT use your general knowledge.
3. Do NOT guess, infer, assume, or invent any information.
4. Every factual statement in your answer MUST be explicitly supported by the context.
4.1. Do NOT infer, derive, assume, or calculate an answer from indirect information.
4.2. Do NOT derive answers from genealogies, sequences, relationships, chronology, or lists.
4.3. If the context does not contain a direct statement supporting the answer, respond exactly:
"لا توجد معلومات كافية في المصادر المتاحة للإجابة عن هذا السؤال."
4.4. Before answering, verify that the answer is explicitly stated in the retrieved context.
5. If the context does not contain enough information to answer the question, respond exactly:
"لا توجد معلومات كافية في المصادر المتاحة للإجابة عن هذا السؤال."
6. If the question is outside the scope of the retrieved Seerah content, respond with the same sentence.
7. If the user asks multiple questions, answer each question separately.
8. If the context supports only part of the question, answer only the supported part and clearly say that the remaining information is not available.
9. Do not add information from memory or from other Islamic sources.
10. Answer in Arabic when the user asks in Arabic.
11. Keep the answer concise and directly related to the question.
12. If the answer is not explicitly supported by the retrieved context, state that the information is not available in the provided sources.
13. Before answering, verify that the exact answer is explicitly stated in the retrieved context. If you cannot find a direct statement supporting the answer, respond exactly:
"لا توجد معلومات كافية في المصادر المتاحة للإجابة عن هذا السؤال."
14. Do not answer with only one or two words. When the context contains enough information, provide at least one complete sentence that clearly explains the answer using the supported details from the context.

Context:
{context}

Question:
{question}

Answer:
"""


class GenerationService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._provider = settings.generation_provider.strip().lower()

        self._anthropic_client: Any = None
        if settings.anthropic_api_key:
            self._anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

    @property
    def is_configured(self) -> bool:
        if self._provider == "ollama":
            return True  # Ollama بيتأكد من نفسه وقت الاستدعاء الفعلي (لو السيرفر مش شغال هيرمي خطأ واضح)
        return self._anthropic_client is not None

    def build_prompt(self, question: str, retrieved: list[dict]) -> str:
        context = "\n\n---\n\n".join(item["text"] for item in retrieved)
        return PROMPT_TEMPLATE.format(context=context, question=question)

    def generate_answer(self, question: str, retrieved: list[dict]) -> str:
        prompt = self.build_prompt(question, retrieved)

        if self._provider == "ollama":
            return self._generate_with_ollama(prompt, retrieved)
        return self._generate_with_anthropic(prompt, retrieved)

    # ------------------------------------------------------------------
    # Ollama (محلي)
    # ------------------------------------------------------------------
    def _generate_with_ollama(self, prompt: str, retrieved: list[dict]) -> str:
        try:
            response = httpx.post(
                f"{self._settings.ollama_base_url}/api/chat",
                json={
                    "model": self._settings.ollama_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()
        except httpx.ConnectError as e:
            logger.error("تعذّر الاتصال بـ Ollama على %s — تأكدي إنه شغال (`ollama serve`).", self._settings.ollama_base_url)
            raise RuntimeError(
                f"تعذّر الاتصال بخادم Ollama على {self._settings.ollama_base_url}. "
                "تأكدي إنه شغال محليًا (شغّلي `ollama serve` أو افتحي تطبيق Ollama)."
            ) from e
        except httpx.HTTPStatusError as e:
            logger.exception("Ollama API error")
            raise RuntimeError(
                f"خطأ من Ollama ({e.response.status_code}): تأكدي إن الموديل '{self._settings.ollama_model}' "
                f"متثبت (`ollama pull {self._settings.ollama_model}`)."
            ) from e

    # ------------------------------------------------------------------
    # Anthropic (سحابي)
    # ------------------------------------------------------------------
    def _generate_with_anthropic(self, prompt: str, retrieved: list[dict]) -> str:
        if self._anthropic_client is None:
            logger.error("ANTHROPIC_API_KEY غير مضبوط.")
            raise RuntimeError(
                "Anthropic API key is not configured."
            )

        try:
            response = self._anthropic_client.messages.create(
                model=self._settings.anthropic_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            text_blocks = [
                b.text for b in response.content
                if b.type == "text"
            ]

            return "\n".join(text_blocks).strip()

        except APIError:
            logger.exception("Anthropic API error")
            raise