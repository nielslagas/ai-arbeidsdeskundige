from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
import uuid
from sqlalchemy import Column # Import Column
from sqlalchemy.dialects.postgresql import JSONB # Import JSONB
from pgvector.sqlalchemy import Vector # Import Vector
from backend.dependencies import engine # Import the database engine

class Case(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(index=True) # Supabase user ID
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    documents: List["Document"] = Relationship(back_populates="case")
    reports: List["GeneratedReport"] = Relationship(back_populates="case")

class Document(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    case_id: uuid.UUID = Field(foreign_key="case.id", index=True)
    file_name: str
    file_path: str # Path in Supabase Storage
    file_type: str # e.g., 'docx', 'txt'
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    processing_status: str = Field(default="uploaded") # e.g., 'uploaded', 'processing', 'completed', 'failed'
    parsed_content: Optional[str] = Field(default=None) # Store extracted text content

    case: Case = Relationship(back_populates="documents")
    chunks: List["Chunk"] = Relationship(back_populates="document")

class ReportTemplate(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    template_schema: dict = Field(sa_column=Column(JSONB)) # Use JSONB for dict
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    reports: List["GeneratedReport"] = Relationship(back_populates="template")

class GeneratedReport(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    case_id: uuid.UUID = Field(foreign_key="case.id", index=True)
    template_id: uuid.UUID = Field(foreign_key="reporttemplate.id", index=True)
    generated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    content: dict = Field(sa_column=Column(JSONB)) # Use JSONB for dict
    generation_status: str = Field(default="pending") # e.g., 'pending', 'generating', 'completed', 'failed'

    case: Case = Relationship(back_populates="reports")
    template: ReportTemplate = Relationship(back_populates="reports")

class Chunk(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    document_id: uuid.UUID = Field(foreign_key="document.id", index=True)
    content: str
    embedding: Vector = Field(sa_column=Column(Vector(1536))) # Change type hint to Vector
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    document: Document = Relationship(back_populates="chunks")

    class Config:
        arbitrary_types_allowed = True
