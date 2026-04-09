from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.api.schemas import SourceCreate, SourceResponse, SearchResponse, AnswerResponse
from llm_wiki.db.models import Source, Document, Chunk
from llm_wiki.db.session import async_session
from llm_wiki.modules.chunking.service import chunk_text
from llm_wiki.modules.embedding.service import generate_embeddings
from llm_wiki.modules.retrieval.service import search_chunks
from llm_wiki.modules.answer.service import generate_answer

router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session


@router.post("/sources", response_model=SourceResponse)
async def create_source(body: SourceCreate, session: AsyncSession = Depends(get_session)):
    source = Source(type=body.type, original_url=body.original_url, title=body.title)
    session.add(source)
    await session.flush()

    if body.content:
        document = Document(
            source_id=source.id,
            title=body.title,
            raw_text=body.content,
            parsed_text=body.content,
        )
        session.add(document)
        await session.flush()

        raw_chunks = chunk_text(body.content)
        chunk_texts = [c["content"] for c in raw_chunks]
        embeddings = await generate_embeddings(chunk_texts)

        for i, c in enumerate(raw_chunks):
            chunk = Chunk(
                document_id=document.id,
                chunk_index=i,
                content=c["content"],
                start_offset=c["start_offset"],
                end_offset=c["end_offset"],
                token_count=len(c["content"]) // 4,
                embedding=embeddings[i],
            )
            session.add(chunk)

        source.status = "parsed"

    await session.commit()
    await session.refresh(source)
    return source


@router.get("/search", response_model=SearchResponse)
async def search(q: str, session: AsyncSession = Depends(get_session)):
    results = await search_chunks(q, session)
    return SearchResponse(query=q, results=results)


@router.get("/ask", response_model=AnswerResponse)
async def ask(q: str, session: AsyncSession = Depends(get_session)):
    chunks = await search_chunks(q, session)
    raw_answer = await generate_answer(q, chunks)
    return AnswerResponse(query=q, **raw_answer)
