from fastapi import APIRouter, HTTPException, Request  # type: ignore[import-not-found]

from app.schemas.query import HealthResponse, QueryRequest, QueryResponse
from app.services.vector_store import VectorStoreNotLoadedError, format_sources

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/query", response_model=QueryResponse)
async def query(request: Request, body: QueryRequest) -> QueryResponse:
    vector_store = request.app.state.vector_store
    generation_service = request.app.state.generation_service
    settings = request.app.state.settings

    try:
        retrieved = vector_store.retrieve(body.question, k=settings.retrieval_top_k)
        for i, item in enumerate(retrieved, 1):
            print(f"\n{'=' * 80}")
            print(f"RETRIEVED RESULT {i}")
            print("METADATA:", item["metadata"])
            print("TEXT:", item["text"][:1000])
    except VectorStoreNotLoadedError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    if not retrieved:
        return QueryResponse(answer="لا توجد معلومات كافية في المصادر للإجابة على هذا السؤال.", sources=[])

    try:
        answer = generation_service.generate_answer(body.question, retrieved)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"فشل توليد الإجابة: {e}") from e

    sources = format_sources(retrieved)
    return QueryResponse(answer=answer, sources=sources)
