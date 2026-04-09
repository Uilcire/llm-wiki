from datetime import datetime 
from pydantic import BaseModel

class SourceCreate(BaseModel):
    type: str
    original_url: str | None = None
    title: str | None = None
    content: str | None = None     # 纯文本内容


class SourceResponse(BaseModel):
    id: int
    type: str
    original_url: str | None
    title: str | None
    status: str
    created_at: datetime


class ChunkResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    distance: float


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]


class Citation(BaseModel):
    chunk_id: int
    quote: str


class AnswerResponse(BaseModel):
    query: str
    answer: str
    supporting_evidence: list[str]
    inferred_points: list[str]
    citations: list[Citation]
    uncertainty: str