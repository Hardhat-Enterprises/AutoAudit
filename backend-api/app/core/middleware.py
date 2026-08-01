import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("api")


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = round(time.time() - start_time, 3)

        logger.info(
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
            }
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related headers to every API response."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        for header_name, header_value in SECURITY_HEADERS.items():
            if header_name not in response.headers:
                response.headers[header_name] = header_value

        return response
