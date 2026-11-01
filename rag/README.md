# AI Quiz Platform — RAG Service

Python FastAPI service for ingestion, retrieval, quiz generation, and evaluation.

## Prerequisites

- Python 3.11+
- pip

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start development server
uvicorn app.main:app --reload --port 8000
```

The RAG service runs at [http://localhost:8000](http://localhost:8000).

API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) during development.

## Health Check

```
GET http://localhost:8000/internal/health
```

## Environment Variables

| Variable | Description |
|---|---|
| `APP_ENV` | Environment (`development`, `production`) |
| `PORT` | Server port (default: 8000) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key |
| `INTERNAL_SERVICE_TOKEN` | Shared secret for service-to-service auth |
| `LLM_PROVIDER` | LLM provider name |
| `LLM_MODEL` | LLM model identifier |
| `LLM_API_KEY` | LLM provider API key |
| `EMBEDDING_PROVIDER` | Embedding provider name |
| `EMBEDDING_MODEL` | Embedding model identifier |
| `EMBEDDING_DIMENSIONS` | Embedding vector dimensions |

## Scripts

| Command | Description |
|---|---|
| `uvicorn app.main:app --reload --port 8000` | Start dev server with hot reload |
| `pytest` | Run tests |
