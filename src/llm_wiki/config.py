from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://bytedance@localhost:5432/llm_wiki"
    openai_api_key: str = ""

    model_config = {"env_prefix": "LLM_WIKI_", "env_file": ".env"}


settings = Settings()
