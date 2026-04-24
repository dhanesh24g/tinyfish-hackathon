# API Service

FastAPI backend for the AI Interview Agent platform.

## Local Development

```bash
cp .env.example .env
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --app-dir src --reload
```

Set `BACKEND_CORS_ORIGINS` to include your frontend URL during local development and on Vercel previews.

## Deploying on Vercel

Set the Vercel project root to `apps/api`.

- entrypoint: `api/index.py`
- app module: `app.main:app`
- config: `vercel.json`

## Backend Layout

```text
apps/api/
  api/          # Vercel entrypoints
  alembic/      # migrations
  evaluation/   # DeepEval checks
  src/app/      # service code
  tests/        # backend tests
```
