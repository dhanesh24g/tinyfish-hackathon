# Web App Contract

Recommended frontend stack for this repo:

- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Vercel deployment

Recommended structure:

```text
apps/web/
  app/
  components/
  features/
  lib/
  public/
  styles/
  tests/
  package.json
  next.config.ts
  tsconfig.json
```

Recommended integration rules:

- Use runtime `API_BASE_URL` for the backend base URL.
- Align local frontend origin with `BACKEND_CORS_ORIGINS` in the backend env.
- Keep API calls isolated in `lib/api/`.
- Keep domain-specific screens in `features/`.
- Add shared types for request and response contracts in `lib/types/`.
- Do not call Supabase directly from the UI for core interview orchestration if the backend already owns that workflow.
- Route all interview, extraction, research, and evaluation actions through the backend API.

Runtime configuration:

- The web app exposes only public runtime config through `/api/config`: `API_BASE_URL`, `SUPABASE_URL`, and `SUPABASE_ANON_KEY`.
- Docker, AWS ECS, Google Cloud Run, Azure, and local runs can inject these as normal runtime environment variables without rebuilding the image.
- On Vercel, rename dashboard variables from `NEXT_PUBLIC_SUPABASE_URL` to `SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` to `SUPABASE_ANON_KEY`, and `NEXT_PUBLIC_API_BASE_URL` to `API_BASE_URL`.
- The `/api/config` route runs as a Vercel serverless function automatically; no extra Vercel config is needed.

Recommended feature folders:

- `features/job-targets/`
- `features/question-bank/`
- `features/interview-session/`
- `features/feedback/`

Recommended API client modules:

- `lib/api/job-targets.ts`
- `lib/api/research.ts`
- `lib/api/interview.ts`
- `lib/api/evaluation.ts`
