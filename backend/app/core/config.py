import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# BASE DIRECTORY
# backend/
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==========================================================
# DATABASE
#
# Priority:
# 1. DATABASE_URL from environment (Render PostgreSQL)
# 2. Local SQLite database (backend/agric_stat.db)
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'agric_stat.db'}"

# Render sometimes provides postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1,
    )

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

FORECAST_DAYS = 30

FORECAST_MODEL = "prophet"

# ==========================================================
# CORS
# ==========================================================

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8080",
]

# ==========================================================
# ENVIRONMENT
# ==========================================================

DEBUG = os.getenv(
    "DEBUG",
    "True",
).lower() == "true"