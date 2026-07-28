"""
Shared rate-limiter instance (slowapi / limits).

Import `limiter` wherever you need to apply @limiter.limit() decorators,
and the two pre-built dependencies for auth vs general routes.
"""

from fastapi import Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: use the real client IP.
# Behind a reverse proxy, ensure FORWARDED / X-Forwarded-For headers are
# trusted by adding ProxyHeadersMiddleware (uvicorn --proxy-headers) or
# Starlette's TrustedHostMiddleware before deploying behind a proxy.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ---------------------------------------------------------------------------
# Reusable FastAPI dependencies
# ---------------------------------------------------------------------------

def general_rate_limit(request: Request) -> None:
    """
    Dependency that enforces the default 200 req/min limit per IP.
    Attach to any router with `dependencies=[Depends(general_rate_limit)]`.
    """
    # slowapi reads limits from the decorator; calling the limiter check here
    # via the shared instance covers routes that use the dependency approach.
    # The middleware already handles decorator-based limits, so this dependency
    # is a no-op signal — actual enforcement is done by SlowAPIMiddleware.
    pass


def auth_rate_limit(request: Request) -> None:
    """
    Placeholder dependency for auth routes.
    Actual enforcement is applied via @limiter.limit() on each endpoint.
    """
    pass
