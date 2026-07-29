"""Runtime configuration, sourced entirely from environment variables.

No secrets are required to run this application. All defaults are safe
for local, offline use.
"""

from __future__ import annotations

import os


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Application settings. Instantiated once at import time."""

    app_name: str = "CHAMP-QN Crypto Readiness Scanner"
    app_version: str = "0.1.0"

    # Internal container port. The published host port is chosen at launch
    # time by scripts/start.sh or scripts/start.ps1, not by this app.
    port: int = _env_int("CHAMPQN_PORT", 8000)
    # Binding all interfaces is intentional: this process runs inside a
    # container, and Docker's port publishing requires the in-container
    # process to listen on 0.0.0.0 to be reachable via the mapped host port.
    host: str = os.environ.get("CHAMPQN_HOST", "0.0.0.0")  # nosec B104

    # Upload safety limits.
    max_upload_bytes: int = _env_int("CHAMPQN_MAX_UPLOAD_BYTES", 2 * 1024 * 1024)  # 2 MiB
    max_assets: int = _env_int("CHAMPQN_MAX_ASSETS", 2000)
    max_algorithms_per_asset: int = _env_int("CHAMPQN_MAX_ALGORITHMS_PER_ASSET", 200)

    # Persistence is OFF by default. Uploaded inventories and their derived
    # findings are processed in memory only and are never written to disk
    # unless an operator explicitly enables this AND supplies a writable
    # directory. The reference implementation ships with this disabled.
    persist_uploads: bool = _env_bool("CHAMPQN_PERSIST_UPLOADS", False)
    persist_dir: str = os.environ.get("CHAMPQN_PERSIST_DIR", "/data")

    log_level: str = os.environ.get("CHAMPQN_LOG_LEVEL", "info")


settings = Settings()
