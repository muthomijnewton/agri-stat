import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================================
# DIRECTORY LAYOUT
#
# This file lives at:  backend/app/core/config.py
#   .parent            backend/app/core/
#   .parent.parent     backend/app/
#   .parent.parent.parent  backend/          <- BACKEND_DIR
# ==========================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

# Load backend/.env explicitly. override=True ensures values from the file
# win over any pre-existing OS environment variables for keys present in
# the file (useful for CI/CD).  Keys absent from the file (like DATABASE_URL
# when using the fallback) are left to the OS environment or the default below.
load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=True)

# ==========================================================
# DATABASE
#
# Priority:
# 1. DATABASE_URL env var set to a non-relative URL (PostgreSQL on Render, etc.)
# 2. Absolute path to backend/agric_stat.db  (SQLite, local dev)
#
# Relative sqlite:/// paths (e.g. from a root .env) are ignored and replaced
# with the absolute path so the server works regardless of CWD.
# ==========================================================

_raw_db_url = os.environ.get("DATABASE_URL", "")


def _is_relative_sqlite(url: str) -> bool:
    """Return True for sqlite:///relative/path (not sqlite:////abs or sqlite://:memory:)."""
    if not url.lower().startswith("sqlite:///"):
        return False
    path_part = url[len("sqlite:///"):]
    return not os.path.isabs(path_part) and path_part not in (":memory:", "")


if not _raw_db_url or _is_relative_sqlite(_raw_db_url):
    # Use an absolute path anchored to the backend directory.
    DATABASE_URL = f"sqlite:///{BACKEND_DIR / 'agric_stat.db'}"
else:
    DATABASE_URL = _raw_db_url

# Render sometimes provides postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==========================================================
# API SETTINGS
# ==========================================================

API_TITLE = "Agricultural Statistics Dashboard API"

API_VERSION = "1.0.0"

API_DESCRIPTION = (
    "Demand forecasting and inventory optimization system "
    "for reducing agricultural produce waste"
)

# ==========================================================
# FORECASTING
# ==========================================================

FORECAST_DAYS = int(os.getenv("FORECAST_DAYS", "30"))

FORECAST_MODEL = os.getenv("FORECAST_MODEL", "prophet")

# ==========================================================
# CORS
#
# ALLOWED_ORIGINS is read from the ALLOWED_ORIGINS environment variable as a
# comma-separated list.  In local dev backend/.env supplies the localhost
# origins; in production the deployment platform (Render, Railway, etc.) sets
# the variable to the live frontend URL(s).
#
# Example backend/.env value:
#   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
#
# Example production value (set in Render / Railway dashboard):
#   ALLOWED_ORIGINS=https://agric-stat.vercel.app
# ==========================================================

_origins_env = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS: list[str] = (
    [o.strip() for o in _origins_env.split(",") if o.strip()]
    if _origins_env
    else [
        # Development fallback — never reached in production if the env var is set.
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
)

# ==========================================================
# ENVIRONMENT
# ==========================================================

# SQL echo is enabled only when DEBUG=true.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ==========================================================
# SECRET KEY  (mandatory)
#
# Must be set via the SECRET_KEY environment variable.
# Generate a secure value with:
#   python -c "import secrets; print(secrets.token_hex(32))"
#
# The application refuses to start if this is missing or left as the
# placeholder, preventing accidental deployment with a weak key.
# ==========================================================

_PLACEHOLDER = "change-this"

_secret = os.getenv("SECRET_KEY", "")

if not _secret or _secret.startswith(_PLACEHOLDER):
    raise RuntimeError(
        "\n\n"
        "  SECRET_KEY is not set or is still the placeholder value.\n"
        "  Generate a secure key and add it to backend/.env:\n\n"
        "    python -c \"import secrets; print(secrets.token_hex(32))\"\n\n"
        "  Then set:  SECRET_KEY=<the generated value>\n"
    )

SECRET_KEY: str = _secret
