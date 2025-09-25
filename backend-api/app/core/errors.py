import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("api")

def problem(
    status: int, title: str, detail: str | None = None, type_: str = "about:blank"
):
    payload = {"type": type_, "title": title, "status": status}
    if detail:
        payload["detail"] = detail

    # Log error in structured format
    if status >= 400:
        logger.error({
            "status": status,
            "title": title,
            "detail": detail
        })

    return JSONResponse(status_code=status, content=payload)


class NotFound(HTTPException):
    """Custom 404 that uses Problem Details format."""
    def __init__(self, resource: str):
        self.resource = resource
        detail = f"{resource} not found"
        super().__init__(status_code=404, detail=detail)
        logger.error({"status": 404, "error": "NotFound", "resource": resource})


# Exception handler for NotFound that uses problem()
async def not_found_handler(request: Request, exc: NotFound):
    return problem(status=404, title="Not Found", detail=exc.detail)
