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
- [ ] Phase 3: quiz generation
- [ ] Phase 4: quiz attempts and evaluation
- [ ] Phase 5: dashboard and analytics
- [ ] Phase 6: hardening and deployment

## Decisions
- Use JavaScript for frontend/backend; Python for AI.
- Use FastAPI for the Python HTTP service.
- Use one Supabase project initially.
- Use a provider adapter so runtime LLM provider/model can be changed via configuration.
- Keep three deployable apps in one Git monorepo.
- Use dependency constraints in `rag/requirements.txt` (`>=`) to support modern Python runtimes (e.g. Python 3.14).
- Support dual-mode authentication: live Supabase Auth with RLS when credentials are configured, with seamless local development fallback when credentials are not yet supplied so development and UI testing remain frictionless.

## Latest work
- Date: 2026-11-01
- Summary: Completed Phase 1 implementation (Database & Authentication).
  - Database: Created `database/migrations/001_create_profiles.sql` defining `profiles` table, RLS policies, automatic trigger on `auth.users`, and `updated_at` trigger. Updated `database/README.md` with setup instructions.
  - Backend: Installed `@supabase/supabase-js` and `zod`. Implemented centralized Supabase service, `requireAuth` JWT middleware, request validation middleware (`validate`), `GET /api/v1/auth/me`, `GET /api/v1/profiles/me`, and `PATCH /api/v1/profiles/me`. Enforced strict body validation disallowing user_id overrides.
  - Frontend: Installed `@supabase/supabase-js` and `@supabase/ssr`. Created reusable browser and server Supabase clients with safe static build fallbacks. Built `AuthContext` supporting signup, login, logout, and session persistence. Built `/login`, `/signup`, `/dashboard` (protected route with profile editing and signout), and updated `/` landing page with dynamic auth navigation.
  - Environment: Created `frontend/.env.local` and `backend/.env` with safe templates.
  - Testing & Security: Implemented 12 automated test cases covering authentication, token verification, unauthorized access, input validation, strict user_id blocking, and cross-user data isolation.
- Files created/modified:
  - `database/migrations/001_create_profiles.sql`, `database/README.md`
  - `backend/`: `src/services/supabase.js`, `src/middleware/auth.js`, `src/middleware/validate.js`, `src/modules/auth/*`, `src/modules/profiles/*`, `src/routes/index.js`, `src/app.js`, `tests/auth_and_profiles.test.js`, `package.json`, `.env`
  - `frontend/`: `lib/supabase/client.js`, `lib/supabase/server.js`, `features/auth/AuthContext.js`, `app/layout.js`, `app/page.js`, `app/login/page.js`, `app/signup/page.js`, `app/dashboard/page.js`, `.env.local`
  - Root: `docs/PROJECT_CONTEXT.md`
- Tests run & exact results:
  - Backend test suite: `npm --prefix backend test` -> 12 passing tests, 0 failures (duration: 932ms):
    - `GET /api/v1/health returns 200 OK`
    - `Accessing protected route GET /api/v1/auth/me without token returns 401 UNAUTHORIZED`
    - `Accessing protected route GET /api/v1/auth/me with malformed Authorization header returns 401`
    - `Accessing protected route GET /api/v1/profiles/me without token returns 401 UNAUTHORIZED`
    - `Accessing protected route PATCH /api/v1/profiles/me without token returns 401 UNAUTHORIZED`
    - `Accessing protected route with an invalid or expired JWT token returns 401 UNAUTHORIZED`
    - `Validation: updateProfileSchema rejects missing or empty display_name`
    - `Security: updateProfileSchema strictly blocks user_id injection in request body`
    - `Security & Controller: getMe returns only claims derived from verified token`
    - `Security & Data Isolation: getProfile queries only user_id from verified token`
    - `Security & Data Isolation: User A cannot update User B profile`
    - `Security: Response never exposes service-role keys or privileged credentials`
  - Frontend production build: `npm --prefix frontend run build` -> Compiled successfully in 72s (all 7 routes statically prerendered with 0 errors).

## Blockers / open decisions
- Provide real Supabase project URL and anon key in `frontend/.env.local` and `backend/.env` for live cloud database synchronization.
- Choose embedding provider/model and confirm vector dimension before creating pgvector schema in Phase 2.

## Next task
Wait for user approval before starting Phase 2 (Notes and Ingestion pipeline).

## Handoff instructions
Before changing code, inspect the actual repository and relevant docs. Update this file after each meaningful task. Record actual commands and test outcomes; do not infer success.
