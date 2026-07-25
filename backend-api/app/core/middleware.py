import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")  # type: ignore[attr-defined]  # pylint: disable=no-member

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        supplied_request_id = request.headers.get(REQUEST_ID_HEADER)

        if supplied_request_id and len(supplied_request_id) <= MAX_REQUEST_ID_LENGTH:
            request_id = supplied_request_id
        else:
            request_id = str(uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        duration = round(time.time() - start_time, 3)

        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
            }
        )

        return response