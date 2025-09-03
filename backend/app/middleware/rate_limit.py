from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Optional

from ..core.config import settings

# Initialize limiter with fallback to in-memory storage if Redis is not available
try:
    # Try to connect to Redis
    import redis
    redis_client = redis.from_url(settings.redis_url, socket_connect_timeout=1)
    redis_client.ping()  # Test connection
    storage_uri = settings.redis_url
except Exception:
    # Fallback to in-memory storage
    storage_uri = "memory://"

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)


def setup_rate_limiting(app: FastAPI):
    """Set up rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler."""
    response = JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "retry_after": str(exc.retry_after)
        }
    )
    response.headers["Retry-After"] = str(exc.retry_after)
    return response


# Rate limiting decorators for specific endpoints
def auth_rate_limit():
    """Rate limit for authentication endpoints."""
    return limiter.limit(f"{settings.login_rate_limit_per_15min}/15minutes")


def password_reset_rate_limit():
    """Rate limit for password reset endpoints."""
    return limiter.limit(f"{settings.password_reset_rate_limit_per_hour}/hour")