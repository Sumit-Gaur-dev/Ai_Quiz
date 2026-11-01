# API Contract

This document is the source of truth for service-to-service and frontend-to-backend contracts. Keep examples synchronized with implementation.

## Conventions
- Public API prefix: `/api/v1`.
- Protected public routes require `Authorization: Bearer <Supabase access token>`.
- `user_id` is derived from verified JWT claims, never trusted from request JSON.
- JSON responses use stable field names; errors use `{ "error": { "code", "message", "requestId" } }`.
- Lists should support pagination.
- Expensive operations should support idempotency keys.

## Public Express routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Backend health |
| POST | `/api/v1/notes` | Create note / start ingestion |
| GET | `/api/v1/notes` | List current user's notes |
| GET | `/api/v1/notes/:noteId` | Get owned note/status |
| DELETE | `/api/v1/notes/:noteId` | Delete owned note and dependent data |
| POST | `/api/v1/notes/:noteId/ingest` | Retry ingestion |
| POST | `/api/v1/quizzes` | Generate quiz |
| GET | `/api/v1/quizzes` | List quizzes |
| GET | `/api/v1/quizzes/:quizId` | Get quiz without answer keys |
| POST | `/api/v1/quizzes/:quizId/attempts` | Start attempt |
| POST | `/api/v1/attempts/:attemptId/submit` | Submit and evaluate |
| GET | `/api/v1/attempts/:attemptId` | Get result |
| GET | `/api/v1/dashboard/summary` | Dashboard aggregates |

## Private FastAPI routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/internal/health` | Health check |
| POST | `/internal/ingest` | Ingest note |
| POST | `/internal/quizzes/generate` | Generate source-grounded quiz |
| POST | `/internal/answers/evaluate` | Evaluate submitted answer(s) |

All `/internal/*` routes require a strong shared service token. They must not be used by the browser.

## Evaluation result shape (conceptual)

```json
{
  "score": 2,
  "max_score": 3,
  "is_correct": false,
  "feedback": "Your answer identifies the main idea but misses one key condition.",
  "missing_concepts": ["..."],
  "correct_concepts": ["..."],
  "evidence_chunk_ids": ["uuid"],
  "confidence": 0.86,
  "status": "evaluated"
}
```

Allowed status values: `evaluated`, `insufficient_context`, `needs_review`. Validate score bounds and evidence IDs on the server.
