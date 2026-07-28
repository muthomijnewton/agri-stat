from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import ALLOWED_ORIGINS, API_TITLE, API_VERSION, API_DESCRIPTION
from app.core.limiter import limiter
from app.api.routes import api_router
from app.db.database import engine, Base
import app.models.models  # noqa: F401 – registers all ORM models

from init_db import init_database, add_default_user, add_sample_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler (replaces deprecated @app.on_event).

    Startup: create tables if they don't exist, then seed default user and
    sample data on first boot.
    """
    init_database()   # creates all tables (no-op if they already exist)
    add_default_user()
    add_sample_data()
    yield
    # (shutdown logic goes here if needed)


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

# Attach the limiter to app.state so slowapi can find it.
app.state.limiter = limiter

# Return HTTP 429 with a JSON body when a limit is exceeded.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# SlowAPIMiddleware intercepts every request and enforces @limiter.limit()
# decorators applied to individual route handlers.
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health check endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
def health_check():
    """Root-level health probe — used by load balancers and the mobile app."""
    return {"status": "healthy"}


@app.get("/api/health", tags=["health"])
def api_health_check():
    """Convenience alias under /api for clients that prefix all calls."""
    return health_check()


# ---------------------------------------------------------------------------
# API routers
# ---------------------------------------------------------------------------

app.include_router(api_router)
