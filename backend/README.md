# AI Quiz Platform — Backend

Node.js + Express API server using JavaScript and ES modules.

## Prerequisites

- Node.js LTS (v18+)
- npm

## Setup

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server (with hot reload)
npm run dev
```

The backend runs at [http://localhost:5000](http://localhost:5000).

## Health Check

```
GET http://localhost:5000/api/v1/health
```

## Environment Variables

| Variable | Description |
|---|---|
| `NODE_ENV` | Environment (`development`, `production`) |
| `PORT` | Server port (default: 5000) |
| `FRONTEND_ORIGIN` | Allowed CORS origin |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase publishable anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key (server only) |
| `RAG_SERVICE_URL` | Internal RAG/AI service URL |
| `INTERNAL_SERVICE_TOKEN` | Shared secret for service-to-service auth |
| `REQUEST_TIMEOUT_MS` | Timeout for outbound requests (default: 60000) |

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start with nodemon (hot reload) |
| `npm start` | Start production server |
| `npm test` | Run tests |
| `npm run lint` | Run linter |

