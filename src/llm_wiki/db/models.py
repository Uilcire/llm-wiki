from datetime import datetime
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from llm_wiki.db.base import Base 
from pgvector.sqlalchemy import Vector                                                                              


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
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))