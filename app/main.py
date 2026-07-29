"""CHAMP-QN Crypto Readiness Scanner — FastAPI application entry point."""

from __future__ import annotations

import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from app import __version__
from app.api.routes import router as api_router
from app.config import settings

_BASE_DIR = pathlib.Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Reference post-quantum cryptography readiness assessment tool. "
        "Part of the CHAMP-QN open-source companion repository."
    ),
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds conservative security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; img-src 'self' data:;"
        )
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.include_router(api_router)

app.mount("/static", StaticFiles(directory=str(_BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(_BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"app_name": settings.app_name, "version": __version__},
    )
