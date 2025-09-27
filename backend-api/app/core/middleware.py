import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        # Process request
        response = await call_next(request)

        duration = round(time.time() - start_time, 3)

        # Log only metadata 
        logger.info({
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration
        })

        return response
