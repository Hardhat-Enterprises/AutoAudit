import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# pylint: disable-next=no-member
logger = logging.getLogger("api")  # type: ignore[attr-defined]

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()

        supplied_request_id = request.headers.get(REQUEST_ID_HEADER)

        if supplied_request_id and len(supplied_request_id) <= MAX_REQUEST_ID_LENGTH:
            request_id = supplied_request_id
        else:
            request_id = str(uuid4())

        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:  # pylint: disable=broad-exception-caught
            duration = round(time.perf_counter() - start_time, 3)

            logger.exception(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration": duration,
                }
            )

            raise

        duration = round(time.perf_counter() - start_time, 3)

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
