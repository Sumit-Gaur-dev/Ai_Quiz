# Project Context — AI Quiz Platform

> This is the concise handoff file for coding-agent/model switches. Keep it current and factual.

## Objective
Build a platform where users upload notes, generate quizzes grounded in those notes, take quizzes, receive evidence-backed feedback, and track performance.

## Architecture
- `frontend/`: Next.js + JavaScript; Vercel.
- `backend/`: Node.js + Express + JavaScript; public application API on Render.
- `rag/`: Python + FastAPI + LangChain; private AI service on Render.
- Supabase Auth + PostgreSQL + pgvector.
- Browser → Express → (Supabase and private FastAPI). Browser never calls FastAPI directly.

## Non-negotiable correctness/security rules
- Verify Supabase JWTs and derive user ID from verified claims.
- Enforce ownership on every note, quiz, attempt, and vector operation.
- Retrieval filters by authenticated `user_id` and authorized `note_id`.
- Uploaded notes are untrusted evidence, not instructions.
- Do not expose answer keys before submission.
- Deterministic scoring for MCQ/true-false; RAG-grounded LLM evaluation for short answers.
- Return `insufficient_context` or `needs_review` rather than fabricate evidence.
- No secrets in frontend or Git.

## Current implementation status
- [x] Phase 0: repository and service skeletons
- [x] Phase 1: database and authentication
- [ ] Phase 2: notes and ingestion
  - [x] Milestone 2.1: RAG service foundation (FastAPI, Google Gen AI SDK, Gemini Embedding 2 with 768 dimensions, LangChain integration base, security middleware, structured logging)
  - [x] Milestone 2.2: Note ingestion, document loaders (PDF/TXT/raw text), text cleaning & chunking
  - [ ] Milestone 2.3: pgvector storage & note retrieval pipeline
- [ ] Phase 3: quiz generation
- [ ] Phase 4: quiz attempts and evaluation
- [ ] Phase 5: dashboard and analytics
- [ ] Phase 6: hardening and deployment

## Decisions
- Use JavaScript for frontend/backend; Python for AI.
- Use FastAPI for the Python HTTP service.
- Use one Supabase project initially.
- Selected embedding model: Google Gemini Embedding 2 (`gemini-embedding-2`) with 768 output dimensions.
- Use the official Google Gen AI Python SDK (`google-genai`) for embedding integration.
- Implement LangChain `Embeddings` base interface in `BaseEmbeddingProvider` for modular interoperability with LangChain document splitters, vector stores, and retrievers.
- Private service authentication via `INTERNAL_SERVICE_TOKEN` supported through both `X-Internal-Service-Token` and `Authorization: Bearer <token>` headers.
- Structured JSON logging with request timing and sensitive credential redaction.
- Document loaders: PyMuPDF for PDF extraction page-by-page preserving 1-indexed page numbers; TXT loader with UTF-8 and Latin-1 fallback; raw text JSON loader.
- Text cleaning: normalizes unprintable control characters, line-break hyphenation (`word-\nbreak`), horizontal whitespace collapsing, and 3+ newline normalization to 2.
- Chunking strategy: LangChain `RecursiveCharacterTextSplitter` with ~1,000 tokens (4,000 characters) and 150 token overlap (600 characters) using hierarchical separators.
- Chunk metadata preservation: `chunk_index`, `page_number`, `source_type`, `note_id`, `user_id`, `source_filename`, `char_count`, `token_count_estimate`.
- Preview endpoints: `POST /internal/ingestion/preview` (multipart file up to 20MB) and `POST /internal/ingestion/preview-text` (raw JSON text). Chunks are previewed without database persistence.

## Latest work
- Date: 2026-11-01
- Summary: Completed Phase 2, Milestone 2.2 (Document Ingestion and Chunking).
  - Dependencies: Added `pymupdf>=1.24.0`, `python-multipart>=0.0.9`, and `langchain-text-splitters>=1.0.0` to `rag/requirements.txt` and verified installation in `.venv`.
  - Document Loaders (`rag/app/ingestion/loaders.py`):
    - PDF extraction with PyMuPDF, preserving 1-indexed page numbers, detecting scanned/empty PDFs, and rejecting password-protected/corrupted files.
    - TXT extraction with UTF-8 decoding and Latin-1 fallback for legacy encodings.
    - Raw text extraction supporting optional note titles.
  - Text Cleaning (`rag/app/ingestion/cleaner.py`):
    - Control character sanitization, line-break hyphenation reconciliation, horizontal whitespace collapsing, and paragraph break normalization (3+ newlines -> 2).
  - Text Chunking (`rag/app/ingestion/chunker.py`):
    - Configured LangChain `RecursiveCharacterTextSplitter` with 4,000 char window (~1,000 tokens) and 600 char overlap (~150 tokens).
    - Sequential chunk indexing and complete provenance metadata attachment.
  - Ingestion Pipeline & Schemas (`rag/app/ingestion/pipeline.py`, `rag/app/schemas/ingestion.py`):
    - Modular preview functions for files and raw text.
    - Pydantic schemas: `ChunkItem`, `DocumentMetadata`, `IngestionPreviewResponse`, `RawTextIngestionRequest`.
  - API Endpoints (`rag/app/api/ingestion.py`):
    - `POST /internal/ingestion/preview`: Multipart upload for `.pdf` and `.txt` files up to 20MB, validates IDs, requires `INTERNAL_SERVICE_TOKEN`.
    - `POST /internal/ingestion/preview-text`: JSON payload for raw text, validates non-empty fields, requires `INTERNAL_SERVICE_TOKEN`.
  - Exception Handling (`rag/app/core/exceptions.py`):
    - Added `UnsupportedMediaTypeException` (415), `PayloadTooLargeException` (413), `EmptyDocumentException` (400), `CorruptedDocumentException` (400), `DocumentExtractionException` (422).
  - Testing (`rag/tests/test_ingestion.py`):
    - Unit and integration tests covering TXT loader, multi-page PDF loader, raw text loader, empty/whitespace handling, corrupted files, unsupported file extensions, chunk overlap detection, metadata preservation, and unauthorized request rejection.
- Files created/modified:
  - `rag/requirements.txt`
  - `rag/app/core/exceptions.py`
  - `rag/app/ingestion/__init__.py`
  - `rag/app/ingestion/cleaner.py`
  - `rag/app/ingestion/loaders.py`
  - `rag/app/ingestion/chunker.py`
  - `rag/app/ingestion/pipeline.py`
  - `rag/app/schemas/ingestion.py`
  - `rag/app/api/ingestion.py`
  - `rag/app/main.py`
  - `rag/tests/test_ingestion.py`
  - `rag/README.md`
  - `docs/PROJECT_CONTEXT.md`
- Tests run & exact results:
  - Pytest suite: `pytest tests -v` -> 29 passed in 6.77s:
    - `tests/test_config.py::test_settings_default_values PASSED`
    - `tests/test_config.py::test_settings_custom_values PASSED`
    - `tests/test_health.py::test_internal_health_endpoint PASSED`
    - `tests/test_ingestion.py::test_clean_text_normalizes_whitespace_and_hyphenation PASSED`
    - `tests/test_ingestion.py::test_clean_text_strips_control_characters PASSED`
    - `tests/test_ingestion.py::test_txt_loader_success PASSED`
    - `tests/test_ingestion.py::test_txt_loader_empty PASSED`
    - `tests/test_ingestion.py::test_pdf_loader_multi_page PASSED`
    - `tests/test_ingestion.py::test_pdf_loader_empty_or_corrupted PASSED`
    - `tests/test_ingestion.py::test_raw_text_loader PASSED`
    - `tests/test_ingestion.py::test_chunk_document_pages_metadata_preservation PASSED`
    - `tests/test_ingestion.py::test_chunk_overlap_detection PASSED`
    - `tests/test_ingestion.py::test_preview_txt_upload_endpoint PASSED`
    - `tests/test_ingestion.py::test_preview_pdf_upload_endpoint PASSED`
    - `tests/test_ingestion.py::test_preview_endpoint_unsupported_file_extension PASSED`
    - `tests/test_ingestion.py::test_preview_endpoint_empty_file PASSED`
    - `tests/test_ingestion.py::test_preview_endpoint_corrupted_pdf PASSED`
    - `tests/test_ingestion.py::test_preview_endpoint_unauthorized PASSED`
    - `tests/test_ingestion.py::test_preview_raw_text_endpoint PASSED`
    - `tests/test_ingestion.py::test_preview_raw_text_empty_content PASSED`
    - `tests/test_ingestion.py::test_preview_raw_text_unauthorized PASSED`
    - `tests/test_provider.py::test_gemini_provider_properties PASSED`
    - `tests/test_provider.py::test_gemini_provider_missing_api_key PASSED`
    - `tests/test_provider.py::test_provider_factory_google PASSED`
    - `tests/test_provider.py::test_provider_factory_unsupported PASSED`
    - `tests/test_security.py::test_protected_route_without_token PASSED`
    - `tests/test_security.py::test_protected_route_with_invalid_token PASSED`
    - `tests/test_security.py::test_protected_route_with_valid_x_header PASSED`
    - `tests/test_security.py::test_protected_route_with_valid_bearer_token PASSED`

## Blockers / open decisions
- None. Ready for Milestone 2.3.

## Next task
Milestone 2.3: Embedding generation & pgvector vector storage for chunks, combined with Supabase database schema and ownership-enforced vector retrieval.
Awaiting user approval before proceeding to Milestone 2.2 (Notes ingestion and text chunking).

## Handoff instructions
Before changing code, inspect the actual repository and relevant docs. Update this file after each meaningful task. Record actual commands and test outcomes; do not infer success.
