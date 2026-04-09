import json

import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.config import settings
from llm_wiki.db.models import (
    Source, Document, Chunk,
    Entity, Claim, WikiEntry, ThoughtEntry,
    Citation, Link,
)

client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a knowledge extraction engine. Given text chunks from a document, extract structured knowledge.

Rules:
- Extract real entities mentioned in the text (people, companies, technologies, projects, topics)
- Extract claims: statements that can be judged true or false
- Extract wiki entries: stable knowledge that could form a wiki page
- Extract thought entries: opinions, questions, analyses, or decisions expressed in the text
- For each extracted item, note which chunk_id it came from
- Be precise. Only extract what is clearly stated or strongly implied.
- Respond in the same language as the source text.
"""

EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_extraction",
        "description": "Submit extracted knowledge objects from the document chunks",
        "parameters": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["person", "company", "project", "topic", "technology"]},
                            "aliases": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "type"],
                    },
                },
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "subject_entity_name": {"type": "string", "description": "Name of the entity this claim is about"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "chunk_id": {"type": "integer"},
                        },
                        "required": ["content", "chunk_id"],
                    },
                },
                "wiki_entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                            "body": {"type": "string"},
                            "scope": {"type": "string", "enum": ["person", "project", "topic"]},
                            "chunk_ids": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["title", "summary", "chunk_ids"],
                    },
                },
                "thought_entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["question", "idea", "decision", "analysis"]},
                            "summary": {"type": "string"},
                            "content": {"type": "string"},
                            "chunk_ids": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["type", "summary", "chunk_ids"],
                    },
                },
                "links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from_name": {"type": "string", "description": "Name/title of the source object"},
                            "to_name": {"type": "string", "description": "Name/title of the target object"},
                            "relation_type": {"type": "string", "enum": ["about", "mentions", "supports", "contradicts", "derived_into"]},
                        },
                        "required": ["from_name", "to_name", "relation_type"],
                    },
                },
            },
            "required": ["entities", "claims", "wiki_entries", "thought_entries", "links"],
        },
    },
}


def _build_chunks_context(chunks: list) -> str:
    parts = []
    for chunk in chunks:
        parts.append(f"[Chunk {chunk.id}]\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


async def _call_extraction(chunks_text: str) -> dict:
    """调用 LLM 抽取结构化知识。"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract knowledge from these chunks:\n\n{chunks_text}"},
        ],
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "function", "function": {"name": "submit_extraction"}},
        temperature=0.2,
    )
    tool_call = response.choices[0].message.tool_calls[0]
    return json.loads(tool_call.function.arguments)


async def extract_from_source(source_id: int, session: AsyncSession) -> dict:
    """对一个 source 的所有 chunks 执行知识抽取，写入数据库。"""

    # 1. 查出这个 source 的所有 chunks
    stmt = (
        select(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.source_id == source_id)
        .order_by(Chunk.chunk_index)
    )
    result = await session.execute(stmt)
    chunks = result.scalars().all()

    if not chunks:
        return {"error": "No chunks found for this source"}

    # 2. 调 LLM 抽取
    chunks_text = _build_chunks_context(chunks)
    extracted = await _call_extraction(chunks_text)

    # 3. 写入 entities，建立 name → id 映射
    entity_map = {}  # name -> entity id
    for e in extracted.get("entities", []):
        entity = Entity(
            name=e["name"],
            type=e["type"],
            aliases={"aliases": e.get("aliases", [])},
        )
        session.add(entity)
        await session.flush()
        entity_map[e["name"]] = entity.id

    # 4. 写入 claims + citations
    for c in extracted.get("claims", []):
        subject_id = entity_map.get(c.get("subject_entity_name"))
        claim = Claim(
            content=c["content"],
            subject_entity_id=subject_id,
            confidence=c.get("confidence"),
        )
        session.add(claim)
        await session.flush()

        citation = Citation(
            target_type="claim",
            target_id=claim.id,
            chunk_id=c["chunk_id"],
        )
        session.add(citation)

    # 5. 写入 wiki_entries + citations
    for w in extracted.get("wiki_entries", []):
        wiki = WikiEntry(
            title=w["title"],
            summary=w["summary"],
            body=w.get("body"),
            scope=w.get("scope"),
        )
        session.add(wiki)
        await session.flush()

        for chunk_id in w.get("chunk_ids", []):
            citation = Citation(
                target_type="wiki_entry",
                target_id=wiki.id,
                chunk_id=chunk_id,
            )
            session.add(citation)

    # 6. 写入 thought_entries + citations
    for t in extracted.get("thought_entries", []):
        thought = ThoughtEntry(
            type=t["type"],
            summary=t["summary"],
            content=t.get("content"),
        )
        session.add(thought)
        await session.flush()

        for chunk_id in t.get("chunk_ids", []):
            citation = Citation(
                target_type="thought_entry",
                target_id=thought.id,
                chunk_id=chunk_id,
            )
            session.add(citation)

    # 7. 写入 links（尽力匹配已创建的对象）
    # v0 只处理 entity 相关的 links
    for lnk in extracted.get("links", []):
        from_id = entity_map.get(lnk["from_name"])
        to_id = entity_map.get(lnk["to_name"])
        if from_id and to_id:
            link = Link(
                from_type="entity",
                from_id=from_id,
                to_type="entity",
                to_id=to_id,
                relation_type=lnk["relation_type"],
            )
            session.add(link)

    # 8. 更新 source 状态
    source_stmt = select(Source).where(Source.id == source_id)
    source = (await session.execute(source_stmt)).scalar_one()
    source.status = "indexed"

    await session.commit()

    return {
        "entities": len(extracted.get("entities", [])),
        "claims": len(extracted.get("claims", [])),
        "wiki_entries": len(extracted.get("wiki_entries", [])),
        "thought_entries": len(extracted.get("thought_entries", [])),
        "links": len(extracted.get("links", [])),
    }
