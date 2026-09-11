"""تحميل الفهرس (FAISS) + المستندات (all_docs.pkl) الناتجة من notebooks/rag_pipeline.ipynb
وبناء Hybrid Retriever (BM25 + Vector) — بنفس منطق backend_loader.py الأصلي،
لكن بمسارات نسبية قابلة للضبط عبر .env، ومُغلَّف داخل class يُحمَّل مرة واحدة
عند إقلاع FastAPI (انظر app/main.py -> lifespan).
"""

import logging
import pickle
from pathlib import Path

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class VectorStoreNotLoadedError(RuntimeError):
    pass


class E5Embeddings(HuggingFaceEmbeddings):
    """نفس الـ class المستخدَم وقت بناء الفهرس في الـ Notebook — لازم يتطابق
    تمامًا (نفس الـ query/passage prefixes) وإلا نتائج الاسترجاع هتبقى غير متسقة."""

    def embed_documents(self, texts):
        texts = [f"passage: {text}" for text in texts]
        return super().embed_documents(texts)

    def embed_query(self, text):
        text = f"query: {text}"
        return super().embed_query(text)


class HybridVectorStore:
    def __init__(
        self,
        vector_store_dir: Path,
        docs_pickle_path: Path,
        embedding_model_name: str,
        internal_k: int = 8,
        bm25_weight: float = 0.45,
        vector_weight: float = 0.55,
    ):
        self.vector_store_dir = vector_store_dir
        self.docs_pickle_path = docs_pickle_path
        self.embedding_model_name = embedding_model_name
        self.internal_k = internal_k
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight

        self._embedding_model: E5Embeddings | None = None
        self._vector_store: FAISS | None = None
        self._bm25_retriever: BM25Retriever | None = None
        self._vector_retriever = None
        self._hybrid_retriever: EnsembleRetriever | None = None

    def load(self) -> None:
        if not self.vector_store_dir.exists():
            raise FileNotFoundError(
                f"مجلد الـ Vector Store غير موجود: {self.vector_store_dir}. "
                "شغّلي notebooks/rag_pipeline.ipynb أولًا لبناء الفهرس."
            )
        if not self.docs_pickle_path.exists():
            raise FileNotFoundError(
                f"ملف all_docs.pkl غير موجود: {self.docs_pickle_path}. "
                "لازم يُصدَّر من خلية الـ Export في الـ Notebook حتى يُعاد بناء BM25."
            )

        logger.info("Loading embedding model %s ...", self.embedding_model_name)
        self._embedding_model = E5Embeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info("Loading FAISS vector store from %s", self.vector_store_dir)
        self._vector_store = FAISS.load_local(
            str(self.vector_store_dir),
            embeddings=self._embedding_model,
            allow_dangerous_deserialization=True,
        )
        logger.info("FAISS index loaded: %d vectors", self._vector_store.index.ntotal)

        logger.info("Loading documents from %s (to rebuild BM25)", self.docs_pickle_path)
        with open(self.docs_pickle_path, "rb") as f:
            all_docs = pickle.load(f)
        logger.info("Documents loaded: %d", len(all_docs))

        # BM25 مالوش persistence API، فبيتبنى تاني من all_docs (سريع، بيحصل مرة واحدة فقط عند الإقلاع)
        self._bm25_retriever = BM25Retriever.from_documents(all_docs)
        self._bm25_retriever.k = self.internal_k

        self._vector_retriever = self._vector_store.as_retriever(search_kwargs={"k": self.internal_k})

        self._hybrid_retriever = EnsembleRetriever(
            retrievers=[self._bm25_retriever, self._vector_retriever],
            weights=[self.bm25_weight, self.vector_weight],
        )
        logger.info("Hybrid retriever (BM25 + Vector) ready.")

    @property
    def is_loaded(self) -> bool:
        return self._hybrid_retriever is not None

    def retrieve(self, question: str, k: int = 6) -> list[dict]:
        if not self.is_loaded:
            raise VectorStoreNotLoadedError("Vector store not loaded")

        internal_k = max(k, self.internal_k)
        self._bm25_retriever.k = internal_k
        self._vector_retriever.search_kwargs["k"] = internal_k

        results = self._hybrid_retriever.invoke(question)[:k]

        return [{"text": doc.page_content, "metadata": doc.metadata} for doc in results]


def _get_page_label(meta: dict) -> int | None:
    page = meta.get("page", -1)
    if page is None or page == -1:
        return None
    return page + 1  # PyPDFLoader بيستخدم ترقيم صفحات من صفر


def format_sources(retrieved: list[dict]) -> list[str]:
    """يحوّل نتائج الاسترجاع إلى قائمة مصادر فريدة قابلة للعرض للمستخدم."""
    sources = []
    for item in retrieved:
        meta = item["metadata"]
        source = meta.get("source", "unknown")
        page_label = _get_page_label(meta)
        if page_label is not None:
            sources.append(f"{source} (صفحة {page_label})")
        else:
            sources.append(source)

    seen = set()
    unique_sources = []
    for s in sources:
        if s not in seen:
            seen.add(s)
            unique_sources.append(s)
    return unique_sources
