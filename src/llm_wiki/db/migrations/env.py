import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from llm_wiki.config import settings
from llm_wiki.db.base import Base
from llm_wiki.db.models import Source, Document, Chunk  # noqa: F401

target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


asyncio.run(run_async_migrations())