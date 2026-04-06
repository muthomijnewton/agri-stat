import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/agric_stat_db")

# API Settings
API_TITLE = "Agricultural Statistics Dashboard API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Demand forecasting and inventory optimization system for reducing agricultural produce waste"

# Forecasting
FORECAST_DAYS = 30
FORECAST_MODEL = "prophet"  # or "arima"

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
]

# Environment
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
