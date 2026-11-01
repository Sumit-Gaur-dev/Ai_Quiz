# Implementation Plan

Work sequentially. Each phase must meet its exit criteria before starting the next.

## Phase 0 — Foundation
- [ ] Create monorepo structure.
- [ ] Add workspace `AGENTS.md` and docs.
- [ ] Create minimal Next.js, Express, and FastAPI applications.
- [ ] Add health endpoints to Express and FastAPI.
- [ ] Add `.env.example`, `.gitignore`, and service setup instructions.
- [ ] Run all three services locally.

Exit: all three services start independently and health checks work.

## Phase 1 — Database and auth
- [ ] Supabase schema and migrations.
- [ ] RLS policies and cross-user tests.
- [ ] Supabase Auth frontend flow.
- [ ] Express JWT verification and ownership middleware.

Exit: users can sign in and cannot access another user's resources.

## Phase 2 — Notes and ingestion
- [ ] Paste text and PDF/TXT upload.
- [ ] Text extraction, chunking, embeddings, pgvector storage.
- [ ] Ingestion status, retry, idempotency, deletion.

Exit: uploaded notes are searchable only by their owner.

## Phase 3 — Quiz generation
- [ ] Provider abstraction and structured schema.
- [ ] Note-scoped retrieval.
- [ ] Generate, validate, and persist questions with evidence IDs.
- [ ] Quiz configuration and preview UI.

Exit: every saved question has traceable note evidence.

## Phase 4 — Quiz attempts and evaluation
- [ ] Attempt lifecycle and answer-key protection.
- [ ] Deterministic objective grading.
- [ ] Evidence-grounded short-answer evaluation.
- [ ] Persist feedback, evidence, and scores.

Exit: complete attempt lifecycle works end-to-end.

## Phase 5 — Dashboard
- [ ] Summary metrics and recent activity.
- [ ] Quiz history and review.
- [ ] Topic-level performance and weak areas.

Exit: dashboard is calculated from persisted attempt data.

## Phase 6 — Production
- [ ] Security, validation, rate limits, timeouts, retries.
- [ ] Tests and error handling.
- [ ] Deploy frontend, backend, AI service, and configure Supabase.
- [ ] Verify production end-to-end workflow.

Exit: new user can sign up, upload notes, generate/take quiz, and review feedback in production.
