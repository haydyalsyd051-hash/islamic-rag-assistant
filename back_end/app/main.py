import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # pyright: ignore[reportMissingImports]

from app.api.routes.query import router as query_router
from app.core.config import get_settings
from app.services.generation import GenerationService
from app.services.vector_store import HybridVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings

    vector_store = HybridVectorStore(
        vector_store_dir=settings.vector_store_path,
        docs_pickle_path=settings.docs_pickle_resolved_path,
        embedding_model_name=settings.embedding_model_name,
        internal_k=settings.retrieval_internal_k,
        bm25_weight=settings.bm25_weight,
        vector_weight=settings.vector_weight,
    )
    try:
        vector_store.load()
    except FileNotFoundError as e:
        logger.error("%s", e)
    app.state.vector_store = vector_store

    app.state.generation_service = GenerationService(settings)
    if settings.generation_provider == "anthropic" and not app.state.generation_service.is_configured:
        logger.warning(
            "ANTHROPIC_API_KEY غير مضبوط في .env — سيعمل الـ endpoint بوضع احتياطي "
            "(إرجاع أفضل قطعة مسترجعة) بدل توليد إجابة كاملة."
        )
    elif settings.generation_provider == "ollama":
        logger.info(
            "التوليد عبر Ollama (%s) على %s — تأكدي إن Ollama شغال محليًا.",
            settings.ollama_model,
            settings.ollama_base_url,
        )

    yield
    # لا حاجة لتنظيف صريح: الموارد (FAISS index في الذاكرة) تُحرَّر تلقائيًا عند إغلاق العملية.


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="RAG API — كتب السيرة النبوية",
        description="نظام استرجاع وتوليد إجابات (RAG) مبني على كتابين في السيرة النبوية.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query_router)
    return app


app = create_app()
