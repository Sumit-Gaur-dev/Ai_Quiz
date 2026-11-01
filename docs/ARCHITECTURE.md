# Architecture Notes

## Service boundaries
- Frontend: presentation, session UX, API calls.
- Express: public API, authentication/authorization, validation, orchestration, persistence.
- FastAPI: ingestion, chunking, embeddings, retrieval, LLM generation/evaluation.
- Supabase: auth, relational persistence, vector persistence, optional private file storage.

## Trust boundaries
1. Browser input is untrusted.
2. Notes are untrusted data and must never override system instructions.
3. Model output is untrusted until schema-validated and semantically checked.
4. FastAPI is private and requires a backend-to-service token.
5. Supabase privileged credentials remain server-side.

## Main data flows
### Ingestion
Create note → process source → chunk → embed → store chunks/vectors → mark status.

### Quiz generation
Authorize note → retrieve note-scoped chunks → generate structured questions → validate evidence and schema → persist quiz/questions.

### Evaluation
Authorize attempt → load answer key server-side → deterministic objective grading / retrieve evidence for short answer → evaluate with rubric → validate → persist feedback.

## Model-provider strategy
Separate chat-model and embedding interfaces. Runtime provider configuration should be environment-driven. Keep embedding model and dimensions stable for a vector collection; changing them requires re-embedding. Log provider/model and prompt version without logging private user content.
