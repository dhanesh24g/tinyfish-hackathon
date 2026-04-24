# AI Interview Agent Monorepo

Monorepo for the AI Interview Agent platform. The repository is structured so backend and frontend can evolve independently while sharing architecture docs, deployment conventions, and integration contracts.

## Repository Layout

```text
apps/
  api/   # FastAPI backend, LangGraph orchestration, web research integration
  web/   # Frontend app boundary for the Vercel UI
docs/    # Shared architecture and onboarding docs
```

## Recommended Team Split

- Backend team works in `apps/api`
- Frontend team works in `apps/web`
- Shared contracts are documented in `docs/architecture.md`

## Industry-Standard Monorepo Guidance

- Keep each deployable app self-contained with its own config, env example, and deployment settings.
- Keep cross-app documentation at the repo root or in `docs/`.
- Treat the backend as the owner of workflow orchestration and persistence.
- Treat the frontend as the owner of user experience and presentation.
- Avoid duplicating business logic across the UI and API.

## Backend App

Backend code now lives in `apps/api`.

Important files:

- [apps/api/src/app/main.py](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/api/src/app/main.py)
- [apps/api/api/index.py](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/api/api/index.py)
- [apps/api/vercel.json](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/api/vercel.json)
- [apps/api/pyproject.toml](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/api/pyproject.toml)

## Frontend App

Frontend should be checked in under `apps/web`.

Recommended stack:

- Next.js App Router
- TypeScript
- Tailwind CSS
- Vercel deployment

Recommended frontend guidance:

- [apps/web/README.md](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/web/README.md)
- [apps/web/.env.example](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/web/.env.example)

## Local Development

Backend:

```bash
cd apps/api
cp .env.example .env
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --app-dir src --reload
```

Helpful shortcuts from the repo root:

```bash
make api-install
make api-migrate
make api-dev
```

## Vercel Deployment

Use separate Vercel projects for cleaner operational boundaries.

- Backend Vercel project root: `apps/api`
- Frontend Vercel project root: `apps/web`

Frontend should call the backend using:

- `NEXT_PUBLIC_API_BASE_URL`

## Environment Files

- Root reference: [.env.example](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/.env.example)
- Backend env template: [apps/api/.env.example](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/api/.env.example)
- Frontend env template: [apps/web/.env.example](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/apps/web/.env.example)

## Additional Docs

- [docs/architecture.md](/Users/parveenshaikh/Study/AI/Courses/Git-Repo/tinyfish-hackathon/docs/architecture.md)
