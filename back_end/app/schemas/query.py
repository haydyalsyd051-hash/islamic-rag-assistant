from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="سؤال المستخدم"
    )


class SourceItem(BaseModel):
    source: list[str]
    page: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    retrieved_context: list[str]


class HealthResponse(BaseModel):
    status: str