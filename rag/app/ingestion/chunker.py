"""Text chunking using LangChain RecursiveCharacterTextSplitter."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ingestion.loaders import DocumentPage

# Character-based approximation for LLM token length (1 token ≈ 4 characters)
DEFAULT_CHUNK_SIZE_TOKENS = 1000
DEFAULT_CHUNK_OVERLAP_TOKENS = 150
CHARS_PER_TOKEN = 4

DEFAULT_CHUNK_SIZE_CHARS = DEFAULT_CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN   # ~4,000 chars
DEFAULT_CHUNK_OVERLAP_CHARS = DEFAULT_CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN # ~600 chars


@dataclass
class DocumentChunk:
    """Represents a discrete, overlapping text chunk with source metadata."""

    chunk_index: int
    content: str
    page_number: Optional[int]
    source_type: str
    note_id: str
    user_id: str
    source_filename: Optional[str]
    char_count: int
    token_count_estimate: int
    metadata: Dict[str, Any] = field(default_factory=dict)


def get_text_splitter(
    chunk_size_chars: int = DEFAULT_CHUNK_SIZE_CHARS,
    chunk_overlap_chars: int = DEFAULT_CHUNK_OVERLAP_CHARS,
) -> RecursiveCharacterTextSplitter:
    """Creates a configured RecursiveCharacterTextSplitter.

    Uses hierarchical separators to preserve paragraphs and sentence boundaries.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        length_function=len,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        keep_separator=True,
    )


def chunk_document_pages(
    pages: List[DocumentPage],
    note_id: str,
    user_id: str,
    source_type: str,
    source_filename: Optional[str] = None,
    chunk_size_chars: int = DEFAULT_CHUNK_SIZE_CHARS,
    chunk_overlap_chars: int = DEFAULT_CHUNK_OVERLAP_CHARS,
) -> List[DocumentChunk]:
    """Splits document pages into ordered, overlapping chunks with rich metadata.

    Preserves page numbers (for multi-page documents like PDFs) and keeps
    strict sequential chunk ordering.
    """
    splitter = get_text_splitter(
        chunk_size_chars=chunk_size_chars,
        chunk_overlap_chars=chunk_overlap_chars,
    )

    chunks: List[DocumentChunk] = []
    current_index = 0

    for page in pages:
        if not page.text or not page.text.strip():
            continue

        raw_chunks = splitter.split_text(page.text)

        for text_chunk in raw_chunks:
            cleaned_chunk = text_chunk.strip()
            if not cleaned_chunk:
                continue

            char_count = len(cleaned_chunk)
            token_estimate = max(1, char_count // CHARS_PER_TOKEN)

            metadata = {
                "chunk_index": current_index,
                "page_number": page.page_number,
                "source_type": source_type,
                "note_id": note_id,
                "user_id": user_id,
                "source_filename": source_filename,
                "char_count": char_count,
                "token_count_estimate": token_estimate,
            }

            chunks.append(
                DocumentChunk(
                    chunk_index=current_index,
                    content=cleaned_chunk,
                    page_number=page.page_number,
                    source_type=source_type,
                    note_id=note_id,
                    user_id=user_id,
                    source_filename=source_filename,
                    char_count=char_count,
                    token_count_estimate=token_estimate,
                    metadata=metadata,
                )
            )
            current_index += 1

    return chunks

