"""Internal API endpoints for document ingestion and chunking preview."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.core.exceptions import (
    AppException,
    PayloadTooLargeException,
    UnsupportedMediaTypeException,
)
from app.core.security import verify_internal_token
from app.ingestion.pipeline import (
    ALLOWED_EXTENSIONS,
    process_document_preview,
    process_raw_text_preview,
)
from app.schemas.ingestion import (
    IngestionPreviewResponse,
    RawTextIngestionRequest,
)

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 Megabytes

router = APIRouter(
    prefix="/internal/ingestion",
    dependencies=[Depends(verify_internal_token)],
    tags=["Ingestion"],
)


@router.post("/preview", response_model=IngestionPreviewResponse)
async def preview_document_upload(
    file: UploadFile = File(..., description="PDF or TXT document file"),
    note_id: str = Form(..., description="Identifier of the note"),
    user_id: str = Form(..., description="Owner user identifier"),
) -> IngestionPreviewResponse:
    """Accepts a multipart PDF or TXT file upload and returns extracted chunks and metadata preview.

    Does not persist chunks in the database.
    """
    clean_note_id = note_id.strip()
    clean_user_id = user_id.strip()

    if not clean_note_id or not clean_user_id:
        raise AppException(
            message="Both note_id and user_id are required and cannot be empty.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    filename = file.filename or "uploaded_file"
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaTypeException(
            f"Unsupported file format '{ext}'. Allowed formats: .pdf, .txt"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise PayloadTooLargeException(
            f"File size ({round(len(file_bytes) / (1024 * 1024), 2)}MB) exceeds the 20MB limit."
        )

    return process_document_preview(
        file_bytes=file_bytes,
        filename=filename,
        note_id=clean_note_id,
        user_id=clean_user_id,
    )


@router.post("/preview-text", response_model=IngestionPreviewResponse)
async def preview_raw_text(
    payload: RawTextIngestionRequest,
) -> IngestionPreviewResponse:
    """Accepts raw text payload in JSON format and returns extracted chunks and metadata preview.

    Does not persist chunks in the database.
    """
    clean_note_id = payload.note_id.strip()
    clean_user_id = payload.user_id.strip()
    clean_text = payload.text.strip()

    if not clean_note_id or not clean_user_id or not clean_text:
        raise AppException(
            message="note_id, user_id, and text must not be empty.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    return process_raw_text_preview(
        text=clean_text,
        note_id=clean_note_id,
        user_id=clean_user_id,
        title=payload.title,
    )

