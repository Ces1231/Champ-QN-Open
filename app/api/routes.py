"""API routes for the CHAMP-QN Crypto Readiness Scanner.

All endpoints operate purely on the request body / uploaded file content.
No uploaded data is written to disk unless CHAMPQN_PERSIST_UPLOADS is
explicitly enabled by the operator (disabled by default, and not
implemented as a write path in this reference version -- see SECURITY.md).
"""

from __future__ import annotations

import json
import pathlib
from typing import Annotated, Literal

import yaml
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import ValidationError

from app import __version__
from app.config import settings
from app.models.inventory import AssessmentResult, Inventory
from app.reporting.report import InventoryTooLargeError, assess_inventory, render_markdown

router = APIRouter()

_EXAMPLES_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "examples"
_SAMPLE_PATH = _EXAMPLES_DIR / "sample-inventory.json"

ReportFormat = Literal["json", "markdown"]
FormatParam = Annotated[ReportFormat, Query(alias="format")]
UploadFileParam = Annotated[UploadFile, File()]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/v1/status")
def status() -> dict[str, object]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": __version__,
        "persist_uploads": settings.persist_uploads,
        "max_upload_bytes": settings.max_upload_bytes,
        "max_assets": settings.max_assets,
    }


def _load_yaml_safely(raw: bytes) -> object:
    """Parse YAML using the safe loader only -- never yaml.load with the
    default loader, which can construct arbitrary Python objects from
    untrusted input."""
    try:
        return yaml.safe_load(raw)
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}") from exc


def _parse_body(raw: bytes, *, filename: str | None) -> dict:
    """Parse an uploaded inventory body as JSON or YAML based on filename hint,
    falling back to trying both if the hint is absent or ambiguous."""
    suffix = pathlib.Path(filename).suffix.lower() if filename else ""

    if suffix in {".yaml", ".yml"}:
        data = _load_yaml_safely(raw)
    elif suffix == ".json":
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}") from exc
    else:
        # No reliable extension -- try JSON first, then safe YAML. Both
        # json.loads and yaml.safe_load can raise UnicodeDecodeError (not
        # just their own format-specific error) on arbitrary binary input,
        # so both attempts must be guarded against both exception types.
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = _load_yaml_safely(raw)

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=422,
            detail="Inventory body must decode to a JSON/YAML object with an 'assets' list.",
        )
    return data


def _build_inventory(data: dict) -> Inventory:
    try:
        return Inventory.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


def _respond(result: AssessmentResult, fmt: ReportFormat):
    if fmt == "markdown":
        return PlainTextResponse(render_markdown(result), media_type="text/markdown")
    return JSONResponse(json.loads(result.model_dump_json()))


@router.post("/api/v1/assess")
def assess(inventory: Inventory, fmt: FormatParam = "json"):
    """Assess an inventory supplied directly as a JSON request body."""
    try:
        result = assess_inventory(inventory)
    except InventoryTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return _respond(result, fmt)


@router.post("/api/v1/assess/upload")
async def assess_upload(file: UploadFileParam, fmt: FormatParam = "json"):
    """Assess an inventory supplied as a JSON or YAML file upload."""
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Uploaded file is {len(raw)} bytes, exceeding the "
                f"{settings.max_upload_bytes}-byte limit."
            ),
        )
    data = _parse_body(raw, filename=file.filename)
    inventory = _build_inventory(data)
    try:
        result = assess_inventory(inventory)
    except InventoryTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return _respond(result, fmt)


@router.post("/api/v1/assess/sample")
def assess_sample(fmt: FormatParam = "json"):
    """Run the assessment against the bundled sample inventory."""
    raw = _SAMPLE_PATH.read_bytes()
    data = _parse_body(raw, filename=str(_SAMPLE_PATH))
    inventory = _build_inventory(data)
    result = assess_inventory(inventory)
    return _respond(result, fmt)


@router.get("/api/v1/sample")
def get_sample() -> dict:
    """Return the bundled sample inventory verbatim (for display or download)."""
    return json.loads(_SAMPLE_PATH.read_text())
