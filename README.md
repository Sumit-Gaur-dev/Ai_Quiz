<<<<<<< HEAD
# Ai_Quiz
An AI RAG (Retrieval-Augmented Generation) Quiz Project
=======
# AI Quiz Platform

An AI-powered learning platform that converts a learner's own notes into quizzes, evaluates answers using only the uploaded source material, and provides actionable feedback and learning analytics.

> **Project principle:** Uploaded notes are the source of truth. The AI must not silently use outside knowledge to generate or grade content.

## 1. Product goals

A user should be able to:

1. Sign up and sign in.
2. Create a notebook and add notes by pasting text or uploading PDF/TXT files.
3. Wait for ingestion to complete and see processing status.
4. Generate a quiz from a selected note or notebook.
5. Configure question count, question types, and difficulty.
6. Take the quiz through a clean, responsive interface.
7. Receive scores, explanations, evidence from their notes, and personalized improvement feedback.
8. Review previous attempts and see dashboard analytics.

### MVP scope

**Build first**
- Supabase authentication.
- Notes: paste text and PDF/TXT upload.
- Note ingestion and embeddings.
- Quiz generation: MCQ, true/false, short answer.
- Quiz taking, submission, scoring, and feedback.
- Dashboard: notes, quizzes, attempts, average score, topic-level weak areas.
- Source-grounded answer evaluation with an insufficient-evidence outcome.

**Defer until the MVP works**
- DOCX/PPTX ingestion, OCR for scanned PDFs, YouTube URLs, collaborative notebooks, spaced repetition, flashcards, timed multiplayer quizzes, payments, organization/team accounts, and advanced adaptive learning.

## 2. Technology stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | Next.js (App Router), JavaScript, React | UI, dashboard, quiz experience |
| UI | Tailwind CSS + a lightweight component library (e.g. shadcn/ui) | Responsive interface |
| Backend | Node.js, Express.js, JavaScript | Auth verification, business logic, API orchestration |
| Main database | Supabase PostgreSQL | Users' app data, notes, quizzes, attempts |
| Authentication | Supabase Auth | Signup, login, session/JWT |
| Vector search | Supabase pgvector | Note chunk embeddings and similarity search |
| AI service | Python, FastAPI | Ingestion, retrieval, quiz generation, evaluation |
| RAG framework | LangChain | Document loaders, splitters, embeddings/vector store, model adapters |
| Validation | Zod (Node), Pydantic (Python) | Validate all external and model-generated data |
| Deployment | Vercel + Render + Supabase | Separate frontend, backend, AI service, database |

Use JavaScript for the frontend and Node backend as requested. Use Python for the AI service. Do not add TypeScript unless explicitly approved.

## 3. Monorepo structure

Create this structure. Keep the three deployable applications independent.

```text
ai-quiz-platform/
├── frontend/                    # Next.js app; Vercel root directory
│   ├── app/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── notes/
│   │   ├── quizzes/
│   │   └── dashboard/
│   ├── lib/
│   ├── public/
│   ├── .env.example
│   └── package.json
│
├── backend/                     # Express API; Render root directory
│   ├── src/
│   │   ├── config/
│   │   ├── middleware/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── notes/
│   │   │   ├── quizzes/
│   │   │   ├── attempts/
│   │   │   └── dashboard/
│   │   ├── services/
│   │   ├── routes/
│   │   ├── utils/
│   │   └── app.js
│   ├── tests/
│   ├── .env.example
│   └── package.json
│
├── rag/                         # FastAPI AI service; Render root directory
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── ingestion/
│   │   ├── retrieval/
│   │   ├── generation/
│   │   ├── evaluation/
│   │   ├── providers/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   ├── migrations/
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACT.md
│   ├── PROJECT_CONTEXT.md
│   └── IMPLEMENTATION_PLAN.md
├── .gitignore
├── AGENTS.md
└── README.md
```

Do not create a complicated shared-workspace/package system in the MVP. The three services communicate over HTTP and share API contracts documented in `docs/API_CONTRACT.md`. Keep cross-service contracts explicit.

## 4. Architecture and service responsibilities

```text
Browser
  |
  v
Next.js frontend (Vercel)
  |
  | HTTPS + Supabase access token
  v
Express backend (Render)
  |                         |
  | SQL / Auth verification | private service-to-service HTTP
  v                         v
Supabase PostgreSQL       FastAPI RAG service (Render)
  |                         |
  | pgvector                 | embedding + LLM provider
  v                         v
Note chunks + vectors      LLM provider API
```

### Frontend

- Render pages and components; do not put secrets in browser code.
- Use a single API client module for Express requests.
- Attach the Supabase access token as `Authorization: Bearer <token>`.
- Handle loading, empty, error, and retry states.
- Do not call the Python service directly from the browser.
- Do not calculate authoritative scores in the browser.

### Node/Express backend

- The public application API and the only entry point used by the frontend.
- Verify Supabase JWTs on protected routes.
- Enforce ownership checks for every note, quiz, and attempt.
- Validate request bodies and query parameters.
- Call the private Python service for ingestion, quiz generation, and answer evaluation.
- Persist application records and return stable response shapes.
- Apply rate limits and request-size limits.
- Never trust `user_id` supplied by the browser; derive it from the verified token.

### Python/FastAPI AI service

- Private service; accept calls only from the backend using a service-to-service secret.
- Validate every request with Pydantic.
- Ingest source text, split it into chunks, create embeddings, and persist chunks/vectors.
- Retrieve only chunks belonging to the requested user and note/notebook.
- Generate schema-constrained quiz questions.
- Evaluate answers against retrieved evidence and the stored reference answer/rubric.
- Return citations/evidence identifiers and explicit uncertainty states.
- Do not own user authentication or expose a public unauthenticated endpoint.

### Supabase

Use one Supabase project initially. PostgreSQL stores normal relational data and pgvector stores embeddings in a vector column. Keep relational data and vector metadata connected using stable IDs.

Use Row Level Security (RLS) for user-owned data. The backend must still perform ownership checks; RLS is not a reason to skip application authorization. Use the service-role/secret key only in trusted server environments. Never expose it in `NEXT_PUBLIC_*` variables.

## 5. Core data model

Implement migrations in `database/migrations/`. Adjust column types and indexes as needed, but preserve ownership and referential integrity.

### `profiles`
- `id UUID PRIMARY KEY REFERENCES auth.users(id)`
- `display_name TEXT`
- `created_at TIMESTAMPTZ`

### `notes`
- `id UUID PRIMARY KEY`
- `user_id UUID NOT NULL REFERENCES auth.users(id)`
- `title TEXT NOT NULL`
- `source_type TEXT` (`paste`, `pdf`, `txt`)
- `source_file_path TEXT NULL`
- `raw_text TEXT` (or protected object storage reference for larger content)
- `ingestion_status TEXT` (`pending`, `processing`, `completed`, `failed`)
- `ingestion_error TEXT NULL`
- `created_at`, `updated_at TIMESTAMPTZ`

### `note_chunks`
- `id UUID PRIMARY KEY`
- `user_id UUID NOT NULL`
- `note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE`
- `chunk_index INTEGER NOT NULL`
- `content TEXT NOT NULL`
- `embedding VECTOR(<DIMENSION>) NOT NULL`
- `metadata JSONB`
- `created_at TIMESTAMPTZ`

Choose an embedding model before creating the vector column. Its vector dimension must match the model output and remain consistent. Changing embedding models/dimensions requires a deliberate re-embedding migration. Add indexes for vector similarity and metadata filters. Use a SQL RPC/function for similarity search with mandatory `user_id` and `note_id` filters.

### `quizzes`
- `id UUID PRIMARY KEY`
- `user_id UUID NOT NULL`
- `note_id UUID NOT NULL REFERENCES notes(id)`
- `title TEXT NOT NULL`
- `description TEXT`
- `difficulty TEXT`
- `question_count INTEGER`
- `generation_status TEXT`
- `created_at TIMESTAMPTZ`

### `questions`
- `id UUID PRIMARY KEY`
- `quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE`
- `question_type TEXT` (`mcq`, `true_false`, `short_answer`)
- `prompt TEXT NOT NULL`
- `options JSONB NULL`
- `correct_answer JSONB NOT NULL`
- `explanation TEXT`
- `source_chunk_ids UUID[]`
- `rubric JSONB NULL`
- `order_index INTEGER NOT NULL`

Never send `correct_answer`, private rubric, or answer keys to the frontend before submission.

### `quiz_attempts`
- `id UUID PRIMARY KEY`
- `user_id UUID NOT NULL`
- `quiz_id UUID NOT NULL REFERENCES quizzes(id)`
- `score NUMERIC`
- `max_score NUMERIC`
- `status TEXT`
- `started_at`, `submitted_at TIMESTAMPTZ`

### `attempt_answers`
- `id UUID PRIMARY KEY`
- `attempt_id UUID NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE`
- `question_id UUID NOT NULL REFERENCES questions(id)`
- `answer JSONB`
- `score NUMERIC`
- `feedback JSONB`
- `evidence_chunk_ids UUID[]`
- `created_at TIMESTAMPTZ`

Add appropriate indexes, foreign keys, unique constraints, timestamps, and RLS policies. Do not store duplicate copies of data without a clear reason.

## 6. RAG and AI design

### Ingestion pipeline

1. Backend creates a note record with `pending` status.
2. Backend sends the note ID, verified user ID, text/file reference, and request ID to the private AI service.
3. AI service extracts text from supported formats.
4. Normalize whitespace and remove obvious extraction noise without changing meaning.
5. Split into chunks using a recursive character splitter. Start with approximately 700–1,000 tokens per chunk and 100–150 tokens overlap; tune with evaluation rather than treating these values as universal.
6. Generate embeddings using one configured embedding model.
7. Store each chunk and vector with `user_id`, `note_id`, `chunk_index`, and source metadata.
8. Mark ingestion completed or failed. Make retries idempotent so a retry does not duplicate chunks.

For large uploads, use Supabase Storage and pass a controlled file reference. Validate file size, MIME type, extension, and ownership. Do not accept arbitrary filesystem paths or arbitrary remote URLs.

### Retrieval

- Similarity search must always filter by both authenticated `user_id` and selected `note_id` (or an explicitly authorized set of note IDs).
- Retrieve a small top-k set, initially 4–6 chunks.
- Consider a similarity threshold and return `insufficient_context` when evidence is weak.
- Keep chunk IDs and source metadata in the returned context.
- Never allow a user to retrieve another user's chunks by changing an ID in a request.
- Consider hybrid search/reranking only after the basic retrieval system is tested.

### Quiz generation

Input:
- note ID
- number of questions
- allowed question types
- difficulty
- optional topic/focus

Process:
1. Retrieve source chunks from that note.
2. Ask the configured LLM to produce structured output matching a Pydantic schema.
3. Require every generated question to include source chunk IDs and a short evidence quote or evidence statement.
4. Validate each question: answer exists, MCQ options are valid, correct option is present, evidence supports the answer, no duplicate questions.
5. Reject or regenerate invalid questions with a bounded retry count.
6. Save valid questions and return quiz metadata. Do not expose answers to the quiz-taking UI.

Do not ask the LLM to invent unsupported facts just to meet the requested question count. Return fewer questions with a clear warning if the notes do not support the requested count.

### Answer evaluation

For each submitted answer:
1. Load the quiz question and reference answer from the database after checking ownership.
2. Retrieve relevant chunks from the original note.
3. Build an evaluation input containing the question, student's answer, reference answer/rubric, and retrieved evidence.
4. Ask the model to judge only against the supplied note evidence and rubric.
5. Require structured output:
   - `score`
   - `max_score`
   - `is_correct`
   - `feedback`
   - `missing_concepts`
   - `correct_concepts`
   - `evidence_chunk_ids`
   - `confidence`
   - `status` (`evaluated`, `insufficient_context`, `needs_review`)
6. Validate score bounds and evidence IDs server-side.
7. Persist the result and return feedback to the frontend.

MCQ and true/false should be deterministically scored by backend code. Use an LLM for short-answer semantic evaluation. This saves tokens, reduces latency, and makes objective grading reproducible.

### Prompt-injection and trust boundaries

Treat uploaded notes as untrusted data, not instructions. The system prompt must explicitly say that document content is evidence only and must not override system instructions. Do not execute code or tools described inside notes. Escape/render note content safely in the UI.

## 7. API contract

All public endpoints are served by Express under `/api/v1`. Protected endpoints require a valid Supabase access token.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Backend health |
| POST | `/api/v1/notes` | Create note / begin ingestion |
| GET | `/api/v1/notes` | List user's notes |
| GET | `/api/v1/notes/:noteId` | Note detail and status |
| DELETE | `/api/v1/notes/:noteId` | Delete owned note and related data |
| POST | `/api/v1/notes/:noteId/ingest` | Retry ingestion |
| POST | `/api/v1/quizzes` | Generate quiz from a note |
| GET | `/api/v1/quizzes` | List user's quizzes |
| GET | `/api/v1/quizzes/:quizId` | Get quiz without answer keys |
| POST | `/api/v1/quizzes/:quizId/attempts` | Start attempt |
| POST | `/api/v1/attempts/:attemptId/submit` | Submit answers and evaluate |
| GET | `/api/v1/attempts/:attemptId` | Attempt result and feedback |
| GET | `/api/v1/dashboard/summary` | Aggregate dashboard metrics |

Use pagination for list endpoints. Add idempotency keys to expensive operations such as ingestion and quiz generation. Return consistent errors:

```json
{
  "error": {
    "code": "NOTE_NOT_READY",
    "message": "This note has not finished processing.",
    "requestId": "request-id"
  }
}
```

### Private Python API

The backend calls the AI service over HTTPS. These routes are not for browser use.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/internal/health` | AI service health |
| POST | `/internal/ingest` | Process note and save chunks |
| POST | `/internal/quizzes/generate` | Generate grounded quiz |
| POST | `/internal/answers/evaluate` | Evaluate one or more answers |

Authenticate every internal request with a strong `INTERNAL_SERVICE_TOKEN` header. Keep it only in backend and AI-service secret environments. Add request IDs, timeouts, bounded retries, and structured logs. Do not log note contents, answers, tokens, or API keys.

Full request/response examples should be maintained in `docs/API_CONTRACT.md`.

## 8. Frontend pages

### Public
- `/` — landing page
- `/login`
- `/signup`

### Authenticated
- `/dashboard` — overview, recent activity, performance cards
- `/notes` — notes list
- `/notes/new` — paste/upload notes
- `/notes/[noteId]` — note detail and ingestion status
- `/quizzes` — generated quizzes
- `/quizzes/new` — quiz configuration
- `/quizzes/[quizId]` — quiz instructions/start
- `/quiz/[quizId]/attempt` — take quiz
- `/attempts/[attemptId]/result` — score, answer review, AI feedback
- `/analytics` — progress and weak-topic insights
- `/settings` — profile and account settings

Design for responsive desktop and mobile. Include skeletons, empty states, errors, confirmation dialogs, and accessible labels. Do not overbuild visual polish before core workflows function.

## 9. Environment variables

Create `.env.example` files containing variable names and safe placeholders only. Never commit real `.env` files.

### `frontend/.env.example`
```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api/v1
```

Only public Supabase URL/anon (publishable) key may be exposed in the browser. Never put service-role keys or model API keys in frontend variables.

### `backend/.env.example`
```env
NODE_ENV=development
PORT=5000
FRONTEND_ORIGIN=http://localhost:3000
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
RAG_SERVICE_URL=http://localhost:8000
INTERNAL_SERVICE_TOKEN=
REQUEST_TIMEOUT_MS=60000
```

Use the Supabase key type recommended by the current Supabase SDK. Keep privileged keys server-side only. Prefer user-scoped Supabase access where practical; if using a service-role key for server operations, enforce ownership checks in application code.

### `rag/.env.example`
```env
APP_ENV=development
PORT=8000
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
INTERNAL_SERVICE_TOKEN=
LLM_PROVIDER=
LLM_MODEL=
LLM_API_KEY=
EMBEDDING_PROVIDER=
EMBEDDING_MODEL=
EMBEDDING_DIMENSIONS=
```

The exact provider-specific variables should be documented when the provider adapter is implemented. Never hardcode model names or API keys in source files.

## 10. Local development

Prerequisites:
- Node.js LTS and npm
- Python version supported by selected LangChain/provider dependencies
- Git
- Supabase project (or local Supabase CLI setup)
- LLM and embedding provider API credentials

Run each application in a separate terminal:

```bash
# Terminal 1 — frontend
cd frontend
npm install
npm run dev

# Terminal 2 — backend
cd backend
npm install
npm run dev

# Terminal 3 — RAG service
cd rag
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Expected local URLs:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`
- AI service: `http://localhost:8000`
- FastAPI docs during development: `http://localhost:8000/docs`

Add `dev`, `test`, and `lint` scripts to each service. Do not assume one root command works until a root task runner is deliberately configured.

## 11. Deployment workflow

Deploy each application separately from the same GitHub monorepo.

### A. Supabase
1. Create one Supabase project.
2. Enable `vector` extension (`pgvector`).
3. Apply SQL migrations in order.
4. Create private Storage bucket for note uploads if file storage is used.
5. Configure RLS policies for all user-owned tables.
6. Configure Auth redirect URLs for local and production frontend domains.
7. Copy project URL and appropriate keys into hosting environment variables.
8. Verify vector dimension and similarity-search SQL function match the chosen embedding model.

### B. Frontend — Vercel
1. Import the GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Select Next.js framework preset.
4. Configure the three frontend environment variables.
5. Set `NEXT_PUBLIC_API_BASE_URL` to the deployed Express URL plus `/api/v1`.
6. Deploy and configure the production domain in Supabase Auth redirect URLs.
7. Configure preview environment variables separately.

### C. Backend — Render
1. Create a Render Web Service connected to the same GitHub repository.
2. Set **Root Directory** to `backend`.
3. Build command: `npm install`
4. Start command: `npm start` (add this script to `package.json`).
5. Add backend environment variables in Render Dashboard.
6. Set `FRONTEND_ORIGIN` to the production frontend origin.
7. Configure CORS to allow only known frontend origins.
8. Deploy and test `/api/v1/health`.

### D. Python RAG service — Render
1. Create another Render Web Service from the same repository.
2. Set **Root Directory** to `rag`.
3. Runtime: Python.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add AI service environment variables.
7. Set `INTERNAL_SERVICE_TOKEN` to the same strong secret configured in the backend.
8. Set `RAG_SERVICE_URL` in backend to the deployed AI service URL.
9. Deploy and test `/internal/health` through an authenticated internal request.

The AI service should not be exposed as a browser-facing public API. Render web services have public service URLs; protect every route with the internal token and consider private networking where supported by the selected plan.

### E. Monorepo deployment behavior
- Vercel project root: `frontend`.
- Render backend root: `backend`.
- Render AI root: `rag`.
- Configure build filters/ignored paths where appropriate so changes to one service do not unnecessarily rebuild unrelated services.
- Changes to root-level shared docs/configuration may require deliberate deployment filter handling.
- Keep deployment configuration and environment variables separate per service.

**Cost note:** Free-tier availability, sleeping/cold starts, build minutes, bandwidth, database limits, and persistent storage rules change. Check the current plans before promising always-on free hosting. A sleeping AI service can cause the first request to be slow; show progress and use sensible timeouts/retries.

## 12. Reliability, security, and quality

- Validate all inputs at the API boundary.
- Verify JWTs and ownership on every protected resource.
- Keep RLS enabled and test cross-user access denial.
- Keep internal AI routes authenticated.
- Set file upload limits and validate file types.
- Add rate limits to generation and evaluation endpoints.
- Add timeouts, bounded retries, and idempotency for expensive AI operations.
- Do not return answer keys before quiz submission.
- Never trust model JSON without schema validation.
- Record model/provider, prompt version, embedding model, and request ID for debugging.
- Avoid logging private source text or secrets.
- Provide deletion that removes a note's chunks, related quizzes/attempts as specified, and stored file.
- Test that deleting a note cannot leave orphaned vector records.
- Add a basic evaluation dataset: notes, expected answerable questions, unanswerable questions, and sample student answers.

### Minimum acceptance tests

1. User A cannot read User B's notes, quizzes, attempts, or vectors.
2. A quiz question can be traced to one or more source chunks.
3. An unsupported question is rejected or flagged instead of hallucinated.
4. An answer that is correct according to general knowledge but unsupported by the notes is not automatically marked correct.
5. MCQ and true/false grading is deterministic.
6. Short-answer feedback includes evidence and missing concepts.
7. A failed ingestion can be retried without duplicate chunks.
8. The frontend never receives answer keys before submission.
9. The app handles model timeout, invalid model output, and insufficient retrieval gracefully.

## 13. Implementation roadmap

Build in small, verifiable phases. Do not ask the coding agent to generate the entire product in one prompt.

### Phase 0 — Planning and repository
- Create monorepo folders and service skeletons.
- Add `AGENTS.md`, docs, `.env.example`, and `.gitignore`.
- Write architecture and API contracts.
- Confirm all three apps start locally.

**Done when:** frontend, backend, and Python service each run independently.

### Phase 1 — Database and authentication
- Create Supabase schema and migrations.
- Configure Supabase Auth.
- Implement frontend login/signup.
- Implement Express JWT middleware and ownership checks.
- Add tests for cross-user access.

**Done when:** users can sign in and securely access only their own resources.

### Phase 2 — Notes and ingestion
- Implement note create/list/detail/delete APIs.
- Build paste-text and PDF/TXT upload UI.
- Implement Python extraction, chunking, embedding, and pgvector storage.
- Add ingestion status and retry behavior.

**Done when:** a user can upload notes and see completed ingestion.

### Phase 3 — Quiz generation
- Implement provider adapter and structured generation schema.
- Implement retrieval restricted to selected note.
- Generate and validate questions.
- Save quiz and questions.
- Build quiz configuration and preview pages.

**Done when:** generated questions are supported by the user's note and saved correctly.

### Phase 4 — Quiz taking and evaluation
- Build attempt lifecycle.
- Hide answer keys from quiz-taking responses.
- Deterministically score objective questions.
- Use RAG + LLM for short-answer grading.
- Save evidence-backed feedback and results.

**Done when:** users can complete a quiz and receive grounded feedback.

### Phase 5 — Dashboard and analytics
- Add recent activity, total quizzes, average score, attempts.
- Add topic-level weak areas based on evaluated answers.
- Add quiz history and review.

**Done when:** dashboard metrics are derived from persisted attempt data.

### Phase 6 — Hardening and deployment
- Add tests, validation, rate limits, error handling, logging.
- Deploy Supabase, backend, AI service, frontend.
- Configure CORS, auth redirect URLs, secrets, and health checks.
- Test complete production workflow.

**Done when:** a new user can sign up, upload notes, generate a quiz, take it, and review grounded feedback in production.

## 14. How to work with Antigravity efficiently

Do not paste the whole README into every prompt. Keep the project open as a workspace and make the repository files the durable source of truth.

### Files that preserve context

- `AGENTS.md`: short, always-relevant project rules and architecture invariants.
- `docs/PROJECT_CONTEXT.md`: current status, decisions, important paths, and next task.
- `docs/ARCHITECTURE.md`: service boundaries and data flow.
- `docs/API_CONTRACT.md`: endpoint and payload contracts.
- `docs/IMPLEMENTATION_PLAN.md`: phases and acceptance criteria.
- Code, tests, migrations, and `.env.example`: actual implementation truth.

After completing a phase, ask the agent to update `docs/PROJECT_CONTEXT.md` with:
- completed work
- files created/changed
- decisions made
- commands/tests run and their results
- known bugs and blockers
- exact next task

Before switching models, ask the current model to update that file. Then switch model in the same workspace and ask the next model to read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, and only the relevant architecture/API docs and source files. Ask it to inspect the actual code before editing.

**Important:** These files reduce repeated explanation, but they do not guarantee that every model has the full conversation or entire repository in its active context. Keep handoff notes concise and verify the workspace is unchanged when switching models.

### Suggested model allocation

Use the model that is most cost-effective and capable for the task; model availability and limits depend on your Antigravity plan and may change.

| Task | Suggested approach |
|---|---|
| Repository scaffolding, repetitive UI, basic CRUD | Faster/cheaper available model |
| Component styling and simple bug fixes | Faster/cheaper available model |
| Database schema, RLS, authorization | Strong reasoning model; review carefully |
| RAG design, retrieval quality, evaluation prompts | Strong reasoning model |
| Cross-service integration and production debugging | Strong reasoning model |
| Code review, security review, architecture decisions | Strongest available model |

Do not use the most expensive model for every small task. Conversely, do not let a weaker model make unreviewed security, data isolation, or grading decisions.

### Prompt template for each task

```text
Read AGENTS.md and docs/PROJECT_CONTEXT.md first.
Read only the architecture/API docs and source files relevant to this task.

Task:
[One small, specific task]

Constraints:
- Preserve the existing architecture and service boundaries.
- Do not rewrite unrelated files.
- Do not add dependencies without explaining why.
- Validate all external inputs.
- Add/update tests for the behavior.
- Do not invent environment variables or API contracts.
- If a decision changes architecture, explain it before implementation.

Before coding:
1. Inspect the existing implementation.
2. Summarize the files you intend to change.
3. Identify assumptions or blockers.

After coding:
1. Summarize files changed.
2. List commands/tests run and actual results.
3. List remaining issues.
4. Update docs/PROJECT_CONTEXT.md with the new project state and next task.
```

### Model-switch handoff prompt

```text
Prepare a handoff for another coding model.

Inspect the actual repository and update docs/PROJECT_CONTEXT.md.
Include:
- Project objective and architecture (briefly)
- Current implementation status by phase
- Important technical decisions and why
- Files/modules changed
- API/database contracts that must not be broken
- Commands and tests run, with results
- Current errors or blockers
- Exact next recommended task
- Files the next model should inspect first

Do not copy the whole codebase into the handoff.
Do not claim tests passed unless you ran them.
```

## 15. First instruction to the coding agent

Start by giving Antigravity this prompt:

```text
We are building the AI Quiz Platform described in README.md.

For now, do NOT implement the entire application.

First:
1. Read README.md carefully.
2. Create the monorepo folder structure.
3. Create AGENTS.md and the docs files specified in the README.
4. Create minimal runnable skeletons for Next.js, Express, and FastAPI.
5. Add .env.example files and a comprehensive .gitignore.
6. Add health endpoints for Express and FastAPI.
7. Add a README in each service with local setup instructions.
8. Ensure all three services can run locally.

Do not implement authentication, database logic, RAG, or quiz generation yet.
Do not invent API keys.
Do not use TypeScript.
Do not deploy anything.

At the end, run the available checks and report the exact results.
Update docs/PROJECT_CONTEXT.md.
Wait for my approval before Phase 1.
```

## 16. Definition of success

The MVP is complete when a user can:

**Sign up → Upload notes → Process embeddings → Generate a source-grounded quiz → Take quiz → Submit answers → Receive evidence-backed AI feedback → View performance dashboard.**
>>>>>>> 5f2e578 (initial commit)
