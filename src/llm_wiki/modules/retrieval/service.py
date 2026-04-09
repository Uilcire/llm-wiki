from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import Chunk
from llm_wiki.modules.embedding.service import generate_embeddings


async def search_chunks(query: str, session: AsyncSession, top_k: int = 5) -> list[dict]:
    """对 query 做 embedding，然后用余弦距离找最相似的 chunks。"""
    # 1. query 转向量
    embeddings = await generate_embeddings([query])
    query_embedding = embeddings[0]

    # 2. 余弦距离搜索，取 top_k 个最近的
    stmt = (
        select(
            Chunk.id,
            Chunk.document_id,
            Chunk.chunk_index,
            Chunk.content,
            Chunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .where(Chunk.embedding.is_not(None))
        .order_by("distance")
        .limit(top_k)
    )
    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "chunk_id": row.id,
            "document_id": row.document_id,
            "chunk_index": row.chunk_index,
            "content": row.content,
            "distance": float(row.distance),
        }
        for row in rows
    ]
