"""إعدادات التطبيق، تُقرأ من متغيرات البيئة / ملف .env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # مزوّد التوليد: "anthropic" أو "ollama"
    generation_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    # مسارات نسبية بشكل افتراضي (بدل المسارات المطلقة بتاعة Windows في backend_loader.py الأصلي)
    # القيمة الافتراضية بتفترض إن الـ backend بيتشغل من مجلد backend/ نفسه
    vector_store_dir: str = "./data/vector_store/faiss_index"
    docs_pickle_path: str = "./data/vector_store/all_docs.pkl"

    embedding_model_name: str = "intfloat/multilingual-e5-base"

    retrieval_top_k: int = 6
    retrieval_internal_k: int = 8  # عدد المرشحين الداخلي لكل من BM25 و Vector قبل الدمج
    bm25_weight: float = 0.45
    vector_weight: float = 0.55

    cors_origins: str = "http://localhost:8501,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def vector_store_path(self) -> Path:
        return Path(self.vector_store_dir).resolve()

    @property
    def docs_pickle_resolved_path(self) -> Path:
        return Path(self.docs_pickle_path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
