from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings.validate_runtime()
    if settings.app_env == "local":
        init_db()
    yield


settings = get_settings()
cors_origins = [item.strip() for item in settings.backend_cors_origins.split(",") if item.strip()]
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for favicons and logos
static_dir = Path(__file__).resolve().parents[2] / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Root endpoint with HTML including favicon links for browser detection
@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Interview Agent API</title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="apple-touch-icon" href="/static/logo.png">
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        h1 { color: #333; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>AI Interview Agent API</h1>
    <p>Welcome to the AI Interview Agent API.</p>
    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/docs">API Documentation</a></li>
    </ul>
</body>
</html>"""

# Favicon.ico endpoint for browsers looking at root
@app.get("/favicon.ico")
def favicon_ico() -> FileResponse:
    favicon_path = static_dir / "favicon.ico"
    if not favicon_path.exists():
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(favicon_path)

# Favicon.png endpoint for browsers looking at root
@app.get("/favicon.png")
def favicon_png() -> FileResponse:
    favicon_path = static_dir / "favicon.png"
    if not favicon_path.exists():
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(favicon_path)

app.include_router(api_router)
