from datetime import datetime

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

from llm_wiki.db.base import Base


# ──────────────────────────────────────────
# 原始层：source → document → chunk
# ──────────────────────────────────────────

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(Text, comment="file | url | text")
    original_url: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'pending'"))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    title: Mapped[str | None] = mapped_column(Text)
    raw_text: Mapped[str | None] = mapped_column(Text)
    parsed_text: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(Text)
    checksum: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    chunk_index: Mapped[int]
    content: Mapped[str] = mapped_column(Text)
    section_title: Mapped[str | None] = mapped_column(Text)
    start_offset: Mapped[int | None]
    end_offset: Mapped[int | None]
    token_count: Mapped[int | None]
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


# ──────────────────────────────────────────
# 知识层：entity, claim, wiki, thought
# ──────────────────────────────────────────

class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text, comment="person | company | project | topic | technology")
    aliases: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    subject_entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id"))
    confidence: Mapped[float | None]
    status: Mapped[str] = mapped_column(Text, server_default=text("'extracted'"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class WikiEntry(Base):
    __tablename__ = "wiki_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'draft'"))
    scope: Mapped[str | None] = mapped_column(Text, comment="person | project | topic")
    valid_from: Mapped[datetime | None]
    valid_to: Mapped[datetime | None]
    version: Mapped[int] = mapped_column(server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class ThoughtEntry(Base):
    __tablename__ = "thought_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(Text, comment="question | idea | decision | analysis")
    summary: Mapped[str] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    author_type: Mapped[str] = mapped_column(Text, server_default=text("'system'"))
    importance: Mapped[float | None]
    related_project: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


# ──────────────────────────────────────────
# 关系层：citation（知识↔证据），link（知识↔知识）
# ──────────────────────────────────────────

class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(Text, comment="claim | wiki_entry | thought_entry")
    target_id: Mapped[int]
    chunk_id: Mapped[int] = mapped_column(ForeignKey("chunks.id"))
    quote_start_offset: Mapped[int | None]
    quote_end_offset: Mapped[int | None]
    evidence_type: Mapped[str] = mapped_column(Text, server_default=text("'direct'"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_type: Mapped[str] = mapped_column(Text, comment="wiki_entry | thought_entry | claim | entity")
    from_id: Mapped[int]
    to_type: Mapped[str] = mapped_column(Text)
    to_id: Mapped[int]
    relation_type: Mapped[str] = mapped_column(Text, comment="about | mentions | supports | contradicts | derived_into")
    confidence: Mapped[float | None]
    status: Mapped[str] = mapped_column(Text, server_default=text("'auto_created'"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
