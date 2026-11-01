"""Pydantic schemas for document ingestion and chunking preview endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChunkItem(BaseModel):
    """Schema representing an individual document chunk."""

    chunk_index: int = Field(description="Zero-based sequential index of the chunk")
    content: str = Field(description="Extracted and cleaned text content of the chunk")
    page_number: Optional[int] = Field(None, description="Source page number (1-indexed for PDFs)")
    char_count: int = Field(description="Character count of this chunk")
    token_count_estimate: int = Field(description="Estimated token count (~4 characters per token)")
    metadata: Dict[str, Any] = Field(description="Provenance metadata for this chunk")


class DocumentMetadata(BaseModel):
    """Schema representing document-level metadata."""

    note_id: str = Field(description="Identifier of the associated note")
    user_id: str = Field(description="Owner user identifier")
    source_type: str = Field(description="Source format: pdf, txt, or raw_text")
    source_filename: Optional[str] = Field(None, description="Original filename if uploaded")
    total_pages: Optional[int] = Field(None, description="Total document pages if applicable")
    title: Optional[str] = Field(None, description="Optional document title")


class IngestionPreviewResponse(BaseModel):
    """Response schema for ingestion preview endpoints."""

    document_metadata: DocumentMetadata = Field(description="Metadata describing the source document")
    total_character_count: int = Field(description="Total characters extracted across all pages")
    total_chunk_count: int = Field(description="Total chunks generated")
    chunks: List[ChunkItem] = Field(description="List of ordered, overlapping chunks with metadata")


class RawTextIngestionRequest(BaseModel):
    """Request payload for raw text ingestion preview."""

    note_id: str = Field(..., min_length=1, description="Identifier of the note")
    user_id: str = Field(..., min_length=1, description="Owner user ID")
    text: str = Field(..., min_length=1, description="Raw source text content")
    title: Optional[str] = Field(None, description="Optional title or note header")

