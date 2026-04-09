import openai

from llm_wiki.config import settings

client = openai.AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """批量生成 embedding 向量。"""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]
