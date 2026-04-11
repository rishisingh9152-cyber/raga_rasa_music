"""Rate limiting service using slowapi"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)

# Predefined rate limit keys
AUTH_RATE_LIMIT = "5/minute"  # 5 requests per minute for auth endpoints
GENERAL_RATE_LIMIT = "100/minute"  # 100 requests per minute for general endpoints
UPLOAD_RATE_LIMIT = "10/hour"  # 10 uploads per hour per IP
