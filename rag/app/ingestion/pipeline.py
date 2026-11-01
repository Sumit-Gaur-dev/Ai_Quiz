"""Ingestion pipeline coordinator connecting loaders, cleaners, and chunkers."""

from typing import List, Optional
from app.core.exceptions import (
    EmptyDocumentException,
    UnsupportedMediaTypeException,
)
from app.ingestion.chunker import chunk_document_pages
from app.ingestion.loaders import (
    DocumentPage,
    load_pdf_bytes,
    load_raw_text,
    load_txt_bytes,
)
from app.schemas.ingestion import (
    ChunkItem,
    DocumentMetadata,
    IngestionPreviewResponse,
)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def process_document_preview(
    file_bytes: bytes,
    filename: str,
    note_id: str,
    user_id: str,
) -> IngestionPreviewResponse:
    """Processes uploaded document bytes (PDF or TXT) and returns chunk preview without persisting."""
    clean_filename = filename.strip()
    ext = ("." + clean_filename.rsplit(".", 1)[-1].lower()) if "." in clean_filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaTypeException(
            f"Unsupported file extension '{ext}'. Only .pdf and .txt are supported."
        )

    if ext == ".pdf":
        pages: List[DocumentPage] = load_pdf_bytes(file_bytes, filename=clean_filename)
        source_type = "pdf"
        total_pages = len(pages)
    else:
        pages = load_txt_bytes(file_bytes, filename=clean_filename)
        source_type = "txt"
        total_pages = 1

    chunks = chunk_document_pages(
        pages=pages,
        note_id=note_id,
        user_id=user_id,
        source_type=source_type,
        source_filename=clean_filename,
    )

    if not chunks:
        raise EmptyDocumentException("No text chunks could be generated from the document.")

    total_chars = sum(len(p.text) for p in pages)

    chunk_items = [
        ChunkItem(
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number,
            char_count=c.char_count,
            token_count_estimate=c.token_count_estimate,
            metadata=c.metadata,
        )
        for c in chunks
    ]

    return IngestionPreviewResponse(
        document_metadata=DocumentMetadata(
            note_id=note_id,
            user_id=user_id,
            source_type=source_type,
            source_filename=clean_filename,
            total_pages=total_pages,
        ),
        total_character_count=total_chars,
        total_chunk_count=len(chunk_items),
        chunks=chunk_items,
    )


def process_raw_text_preview(
    text: str,
    note_id: str,
    user_id: str,
    title: Optional[str] = None,
) -> IngestionPreviewResponse:
    """Processes raw string text input and returns chunk preview without persisting."""
    pages = load_raw_text(text, title=title)

    chunks = chunk_document_pages(
        pages=pages,
        note_id=note_id,
        user_id=user_id,
        source_type="raw_text",
        source_filename=None,
    )

    if not chunks:
        raise EmptyDocumentException("No text chunks could be generated from the submitted text.")

    total_chars = sum(len(p.text) for p in pages)

    chunk_items = [
        ChunkItem(
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number,
            char_count=c.char_count,
            token_count_estimate=c.token_count_estimate,
            metadata=c.metadata,
        )
        for c in chunks
    ]

    return IngestionPreviewResponse(
        document_metadata=DocumentMetadata(
            note_id=note_id,
            user_id=user_id,
            source_type="raw_text",
            source_filename=None,
            total_pages=1,
            title=title,
        ),
        total_character_count=total_chars,
        total_chunk_count=len(chunk_items),
        chunks=chunk_items,
    )

