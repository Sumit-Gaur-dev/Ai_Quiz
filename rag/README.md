# AI Quiz Platform — RAG Service

Python FastAPI service for ingestion, retrieval, quiz generation, and answer evaluation.

## Architecture

- **Framework**: FastAPI (ASGI)
- **AI / LLM SDK**: Official Google Gen AI Python SDK (`google-genai`)
- **Embedding Model**: Google Gemini Embedding 2 (`gemini-embedding-2`), output dimensionality: `768`
- **Framework Abstraction**: LangChain core integration (`BaseEmbeddingProvider` conforming to `langchain_core.embeddings.Embeddings`)
- **Configuration**: Pydantic Settings with automatic `.env` loading
- **Security**: Service-to-service token authentication (`INTERNAL_SERVICE_TOKEN`)
- **Logging**: Structured JSON logging with request timing and sensitive credential redaction

## Prerequisites

- Python 3.11+
- pip

## Setup

```bash
# Navigate to rag directory
cd rag

# Create virtual environment (if not already created)
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env with your credentials:
# - GEMINI_API_KEY
# - INTERNAL_SERVICE_TOKEN (must match backend's INTERNAL_SERVICE_TOKEN)

# Start development server
uvicorn app.main:app --reload --port 8000
```

The RAG service runs locally at [http://localhost:8000](http://localhost:8000).
Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Health & Internal Endpoints

### Health Check (Public / Monitoring)
```http
GET /internal/health
```
Response:
```json
{
  "status": "ok",
  "service": "ai-quiz-rag",
  "timestamp": "2026-11-01T16:20:44.645206+00:00",
  "embedding_provider": "google",
  "embedding_model": "gemini-embedding-2",
  "embedding_dimensions": 768
}
```

### Protected Internal Endpoints
Protected `/internal/*` routes require authentication via header:
- `X-Internal-Service-Token: <token>` OR
- `Authorization: Bearer <token>`

### Document Ingestion & Chunking Preview

#### 1. Multipart Document Upload Preview
```http
POST /internal/ingestion/preview
Content-Type: multipart/form-data
```
**Form Data**:
- `file`: PDF or TXT binary file (Max 20MB)
- `note_id`: Note UUID or string identifier
- `user_id`: User UUID or string identifier

**Response (200 OK)**:
```json
{
  "document_metadata": {
    "note_id": "note_123",
    "user_id": "usr_456",
    "source_type": "pdf",
    "source_filename": "lecture_notes.pdf",
    "total_pages": 4,
    "title": null
  },
  "total_character_count": 8200,
  "total_chunk_count": 3,
  "chunks": [
    {
      "chunk_index": 0,
      "content": "Cleaned chunk text...",
      "page_number": 1,
      "char_count": 3840,
      "token_count_estimate": 960,
      "metadata": {
        "chunk_index": 0,
        "page_number": 1,
        "source_type": "pdf",
        "note_id": "note_123",
        "user_id": "usr_456",
        "source_filename": "lecture_notes.pdf",
        "char_count": 3840,
        "token_count_estimate": 960
      }
    }
  ]
}
```

#### 2. Raw Text Preview
```http
POST /internal/ingestion/preview-text
Content-Type: application/json
```
**Request Body**:
```json
{
  "note_id": "note_123",
  "user_id": "usr_456",
  "text": "Raw notes text content...",
  "title": "Optional Note Title"
}
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | Application environment (`development`, `production`) | `development` |
| `PORT` | Service port | `8000` |
| `LOG_LEVEL` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `INTERNAL_SERVICE_TOKEN` | Shared secret for service-to-service auth | *(Required)* |
| `GEMINI_API_KEY` | Google Gemini API Key | *(Required)* |
| `EMBEDDING_PROVIDER` | Embedding provider name | `google` |
| `EMBEDDING_MODEL` | Embedding model identifier | `gemini-embedding-2` |
| `EMBEDDING_DIMENSIONS` | Vector output dimensions | `768` |
| `SUPABASE_URL` | Supabase project URL (for vector storage) | *(Optional in Milestone 2.1)* |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key | *(Optional in Milestone 2.1)* |

## Testing

Run the test suite using pytest:

```bash
cd rag
.venv\Scripts\python.exe -m pytest tests -v
```
