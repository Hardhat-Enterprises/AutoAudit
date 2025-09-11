from fastapi import HTTPException
from fastapi.responses import JSONResponse


def problem(
    status: int, title: str, detail: str | None = None, type_: str = "about:blank"
):
    payload = {"type": type_, "title": title, "status": status}
    if detail:
        payload["detail"] = detail
    return JSONResponse(status_code=status, content=payload)


class NotFound(HTTPException):
    def __init__(self, resource: str):
        super().__init__(status_code=404, detail=f"{resource} not found")
