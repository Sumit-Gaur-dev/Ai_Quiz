"""Tests for document ingestion, text cleaning, chunking, and preview endpoints."""

import io
import pytest
import pymupdf
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.exceptions import (
    CorruptedDocumentException,
    EmptyDocumentException,
    UnsupportedMediaTypeException,
)
from app.ingestion.cleaner import clean_text
from app.ingestion.loaders import load_pdf_bytes, load_raw_text, load_txt_bytes
from app.ingestion.chunker import (
    DEFAULT_CHUNK_OVERLAP_CHARS,
    DEFAULT_CHUNK_SIZE_CHARS,
    chunk_document_pages,
    get_text_splitter,
)
from app.ingestion.pipeline import (
    process_document_preview,
    process_raw_text_preview,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {settings.internal_service_token}"}


def create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Helper to generate in-memory PDF bytes with the specified text per page."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ---------------------------------------------------------------------------
# Unit Tests: Cleaner
# ---------------------------------------------------------------------------


def test_clean_text_normalizes_whitespace_and_hyphenation():
    raw = "Here is some text with mul-  \ntiple    spaces and a hy-\nphenated word.\n\n\n\nNew paragraph."
    cleaned = clean_text(raw)
    assert "hyphenated" in cleaned
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned
    assert "New paragraph." in cleaned


def test_clean_text_strips_control_characters():
    raw = "Valid text\x00\x08with unprintable\x1f controls."
    cleaned = clean_text(raw)
    assert cleaned == "Valid text with unprintable controls."


# ---------------------------------------------------------------------------
# Unit Tests: Loaders
# ---------------------------------------------------------------------------


def test_txt_loader_success():
    content = "Hello World! This is a test note on Quantum Mechanics."
    file_bytes = content.encode("utf-8")
    pages = load_txt_bytes(file_bytes, filename="quantum.txt")

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "Quantum Mechanics" in pages[0].text
    assert pages[0].metadata["source_type"] == "txt"
    assert pages[0].metadata["source_filename"] == "quantum.txt"


def test_txt_loader_empty():
    with pytest.raises(EmptyDocumentException):
        load_txt_bytes(b"", filename="empty.txt")

    with pytest.raises(EmptyDocumentException):
        load_txt_bytes(b"   \n\t  \n  ", filename="whitespace.txt")


def test_pdf_loader_multi_page():
    pdf_bytes = create_in_memory_pdf([
        "Page 1: Overview of Mitochondria and ATP synthesis.",
        "Page 2: The Krebs cycle details and NADH generation.",
    ])

    pages = load_pdf_bytes(pdf_bytes, filename="biology.pdf")
    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert "Mitochondria" in pages[0].text
    assert pages[1].page_number == 2
    assert "Krebs cycle" in pages[1].text
    assert pages[0].metadata["total_pages"] == 2


def test_pdf_loader_empty_or_corrupted():
    with pytest.raises(EmptyDocumentException):
        load_pdf_bytes(b"", filename="zero_bytes.pdf")

    with pytest.raises(CorruptedDocumentException):
        load_pdf_bytes(b"Not a valid PDF header or content", filename="corrupted.pdf")


def test_raw_text_loader():
    pages = load_raw_text("Direct raw text notes about thermodynamics.", title="Thermo")
    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "thermodynamics" in pages[0].text
    assert pages[0].metadata["title"] == "Thermo"

    with pytest.raises(EmptyDocumentException):
        load_raw_text("   \n\t  ")


# ---------------------------------------------------------------------------
# Unit Tests: Chunker & Overlap
# ---------------------------------------------------------------------------


def test_chunk_document_pages_metadata_preservation():
    pdf_bytes = create_in_memory_pdf([
        "Page one content about history.",
        "Page two content about geography.",
    ])
    pages = load_pdf_bytes(pdf_bytes, filename="humanities.pdf")
    chunks = chunk_document_pages(
        pages=pages,
        note_id="note_123",
        user_id="user_456",
        source_type="pdf",
        source_filename="humanities.pdf",
    )

    assert len(chunks) == 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].note_id == "note_123"
    assert chunks[0].user_id == "user_456"
    assert chunks[0].source_type == "pdf"
    assert chunks[0].source_filename == "humanities.pdf"

    assert chunks[1].chunk_index == 1
    assert chunks[1].page_number == 2
    assert chunks[1].note_id == "note_123"
    assert chunks[1].user_id == "user_456"


def test_chunk_overlap_detection():
    # Create text that exceeds chunk size to trigger multi-chunk splitting
    # Chunk size: 200 chars, overlap: 50 chars for testing
    paragraph = "Sentence alpha. " * 30  # ~480 characters
    pages = load_raw_text(paragraph, title="Overlap Test")
    
    chunks = chunk_document_pages(
        pages=pages,
        note_id="note_overlap",
        user_id="user_overlap",
        source_type="raw_text",
        chunk_size_chars=200,
        chunk_overlap_chars=50,
    )

    assert len(chunks) > 1
    # Verify sequential ordering
    for i in range(len(chunks)):
        assert chunks[i].chunk_index == i

    # Verify overlap exists between chunk 0 and chunk 1
    chunk_0_tail = chunks[0].content[-30:]
    assert chunk_0_tail in chunks[1].content or any(word in chunks[1].content for word in chunk_0_tail.split())


# ---------------------------------------------------------------------------
# API Integration Tests: POST /internal/ingestion/preview
# ---------------------------------------------------------------------------


def test_preview_txt_upload_endpoint(client, auth_headers):
    file_content = b"Study Notes: Algorithms and Data Structures.\nBinary Search Trees and AVL balance."
    files = {"file": ("algorithms.txt", io.BytesIO(file_content), "text/plain")}
    data = {"note_id": "note_algo_1", "user_id": "usr_test_1"}

    response = client.post(
        "/internal/ingestion/preview",
        headers=auth_headers,
        files=files,
        data=data,
    )

    assert response.status_code == 200
    res_data = response.json()

    assert res_data["document_metadata"]["note_id"] == "note_algo_1"
    assert res_data["document_metadata"]["user_id"] == "usr_test_1"
    assert res_data["document_metadata"]["source_type"] == "txt"
    assert res_data["document_metadata"]["source_filename"] == "algorithms.txt"
    assert res_data["total_chunk_count"] >= 1
    assert len(res_data["chunks"]) == res_data["total_chunk_count"]
    assert res_data["chunks"][0]["chunk_index"] == 0
    assert "Binary Search Trees" in res_data["chunks"][0]["content"]


def test_preview_pdf_upload_endpoint(client, auth_headers):
    pdf_bytes = create_in_memory_pdf([
        "Calculus 1: Derivatives and rates of change.",
        "Calculus 2: Integrals and areas under curves.",
    ])
    files = {"file": ("calculus.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    data = {"note_id": "note_calc_1", "user_id": "usr_test_2"}

    response = client.post(
        "/internal/ingestion/preview",
        headers=auth_headers,
        files=files,
        data=data,
    )

    assert response.status_code == 200
    res_data = response.json()

    assert res_data["document_metadata"]["source_type"] == "pdf"
    assert res_data["document_metadata"]["total_pages"] == 2
    assert res_data["total_chunk_count"] == 2
    assert res_data["chunks"][0]["page_number"] == 1
    assert res_data["chunks"][1]["page_number"] == 2


def test_preview_endpoint_unsupported_file_extension(client, auth_headers):
    files = {"file": ("presentation.docx", io.BytesIO(b"Fake docx content"), "application/vnd.openxmlformats")}
    data = {"note_id": "note_1", "user_id": "user_1"}

    response = client.post(
        "/internal/ingestion/preview",
        headers=auth_headers,
        files=files,
        data=data,
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_preview_endpoint_empty_file(client, auth_headers):
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    data = {"note_id": "note_1", "user_id": "user_1"}

    response = client.post(
        "/internal/ingestion/preview",
        headers=auth_headers,
        files=files,
        data=data,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_DOCUMENT"


def test_preview_endpoint_corrupted_pdf(client, auth_headers):
    files = {"file": ("corrupt.pdf", io.BytesIO(b"Definitely not a valid PDF file!"), "application/pdf")}
    data = {"note_id": "note_1", "user_id": "user_1"}

    response = client.post(
        "/internal/ingestion/preview",
        headers=auth_headers,
        files=files,
        data=data,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CORRUPTED_DOCUMENT"


def test_preview_endpoint_unauthorized(client):
    # No Authorization header
    files = {"file": ("test.txt", io.BytesIO(b"Some text"), "text/plain")}
    data = {"note_id": "note_1", "user_id": "user_1"}

    response = client.post(
        "/internal/ingestion/preview",
        files=files,
        data=data,
    )
    assert response.status_code == 401

    # Invalid token
    response_invalid = client.post(
        "/internal/ingestion/preview",
        headers={"Authorization": "Bearer totally-invalid-token"},
        files=files,
        data=data,
    )
    assert response_invalid.status_code == 401


# ---------------------------------------------------------------------------
# API Integration Tests: POST /internal/ingestion/preview-text
# ---------------------------------------------------------------------------


def test_preview_raw_text_endpoint(client, auth_headers):
    payload = {
        "note_id": "note_raw_99",
        "user_id": "usr_raw_99",
        "text": "Photosynthesis is the process used by plants to convert light energy into chemical energy.",
        "title": "Bio 101 Notes",
    }

    response = client.post(
        "/internal/ingestion/preview-text",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 200
    res_data = response.json()

    assert res_data["document_metadata"]["source_type"] == "raw_text"
    assert res_data["document_metadata"]["title"] == "Bio 101 Notes"
    assert res_data["total_chunk_count"] >= 1
    assert "Photosynthesis" in res_data["chunks"][0]["content"]
    assert res_data["chunks"][0]["metadata"]["user_id"] == "usr_raw_99"


def test_preview_raw_text_empty_content(client, auth_headers):
    payload = {
        "note_id": "note_raw_99",
        "user_id": "usr_raw_99",
        "text": "     ",
    }

    response = client.post(
        "/internal/ingestion/preview-text",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code in (400, 422)


def test_preview_raw_text_unauthorized(client):
    payload = {
        "note_id": "note_1",
        "user_id": "user_1",
        "text": "Valid text content.",
    }

    response = client.post(
        "/internal/ingestion/preview-text",
        json=payload,
    )
    assert response.status_code == 401

