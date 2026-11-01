"""Document loaders for PDF, TXT, and raw text sources using PyMuPDF and standard libraries."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pymupdf
from app.core.exceptions import (
    CorruptedDocumentException,
    DocumentExtractionException,
    EmptyDocumentException,
)
from app.ingestion.cleaner import clean_text


@dataclass
class DocumentPage:
    """Represents a discrete page or section extracted from a document."""

    page_number: Optional[int]
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def load_pdf_bytes(
    file_bytes: bytes,
    filename: Optional[str] = None,
) -> List[DocumentPage]:
    """Extracts text page-by-page from raw PDF bytes using PyMuPDF.

    Preserves page numbers (1-indexed) and raises appropriate exceptions
    for empty, corrupted, or password-protected files.
    """
    if not file_bytes:
        raise EmptyDocumentException("Uploaded PDF file is empty (0 bytes).")

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise CorruptedDocumentException(
            f"Failed to open PDF document: {str(exc)}"
        ) from exc

    try:
        if doc.is_encrypted:
            raise CorruptedDocumentException(
                "Encrypted or password-protected PDF files are not supported."
            )

        total_pages = len(doc)
        if total_pages == 0:
            raise EmptyDocumentException("The PDF document contains 0 pages.")

        pages: List[DocumentPage] = []
        total_extracted_chars = 0

        for page_idx in range(total_pages):
            page = doc[page_idx]
            raw_page_text = page.get_text("text")
            cleaned_page_text = clean_text(raw_page_text)

            total_extracted_chars += len(cleaned_page_text)

            pages.append(
                DocumentPage(
                    page_number=page_idx + 1,
                    text=cleaned_page_text,
                    metadata={
                        "source_type": "pdf",
                        "page_number": page_idx + 1,
                        "total_pages": total_pages,
                        "source_filename": filename,
                    },
                )
            )

        if total_extracted_chars == 0:
            raise EmptyDocumentException(
                "The PDF document contains no extractable text. Scanned or image-only PDFs require OCR."
            )

        return pages
    except (EmptyDocumentException, CorruptedDocumentException):
        raise
    except Exception as exc:
        raise DocumentExtractionException(
            f"Error during PDF text extraction: {str(exc)}"
        ) from exc
    finally:
        doc.close()


def load_txt_bytes(
    file_bytes: bytes,
    filename: Optional[str] = None,
) -> List[DocumentPage]:
    """Decodes and extracts text from TXT file bytes."""
    if not file_bytes:
        raise EmptyDocumentException("Uploaded text file is empty (0 bytes).")

    try:
        raw_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Fallback for Windows-1252 or Latin-1 encodings
            raw_text = file_bytes.decode("latin-1")
        except Exception as exc:
            raise CorruptedDocumentException(
                f"Failed to decode text file with UTF-8 or Latin-1: {str(exc)}"
            ) from exc

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise EmptyDocumentException("Text document contains no readable text.")

    return [
        DocumentPage(
            page_number=1,
            text=cleaned,
            metadata={
                "source_type": "txt",
                "page_number": 1,
                "total_pages": 1,
                "source_filename": filename,
            },
        )
    ]


def load_raw_text(
    raw_text: str,
    title: Optional[str] = None,
) -> List[DocumentPage]:
    """Loads and cleans raw text provided directly via API."""
    if not raw_text or not raw_text.strip():
        raise EmptyDocumentException("Submitted raw text is empty.")

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise EmptyDocumentException("Submitted text contains no readable characters.")

    return [
        DocumentPage(
            page_number=1,
            text=cleaned,
            metadata={
                "source_type": "raw_text",
                "page_number": 1,
                "total_pages": 1,
                "title": title,
            },
        )
    ]

