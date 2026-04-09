import json

import openai

from llm_wiki.config import settings

client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a knowledge assistant. Answer the user's question based ONLY on the provided context chunks.

Rules:
- If the context doesn't contain enough information, say so in the answer
- supporting_evidence must be exact quotes, not paraphrases
- inferred_points are things you reasoned about but aren't directly stated
- Always cite which chunk_id the evidence comes from
- Respond in the same language as the user's question
"""

# 定义一个虚拟工具，LLM 会被强制按这个 schema 返回结构化数据
ANSWER_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_answer",
        "description": "Submit a structured answer based on the retrieved context chunks",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Direct answer to the user's question",
                },
                "supporting_evidence": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exact quotes from the context that support the answer",
                },
                "inferred_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Points inferred but not directly stated in the context",
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "chunk_id": {"type": "integer"},
                            "quote": {"type": "string"},
                        },
                        "required": ["chunk_id", "quote"],
                    },
                    "description": "References to specific chunks with relevant quotes",
                },
                "uncertainty": {
                    "type": "string",
                    "description": "What is uncertain or missing, or 'None' if fully confident",
                },
            },
            "required": ["answer", "supporting_evidence", "inferred_points", "citations", "uncertainty"],
        },
    },
}


def _build_context(chunks: list[dict]) -> str:
    """把搜索到的 chunks 格式化成 LLM 能读的上下文。"""
    parts = []
    for chunk in chunks:
        parts.append(f"[Chunk {chunk['chunk_id']}]\n{chunk['content']}")
    return "\n\n---\n\n".join(parts)


async def generate_answer(query: str, chunks: list[dict]) -> dict:
    """基于检索到的 chunks 生成结构化回答。"""
    context = _build_context(chunks)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        tools=[ANSWER_TOOL],
        tool_choice={"type": "function", "function": {"name": "submit_answer"}},
        temperature=0.3,
    )

    # LLM 返回的是 tool call，从 arguments 里取结构化数据
    tool_call = response.choices[0].message.tool_calls[0]
    return json.loads(tool_call.function.arguments)
