"""Response model for checking the health status of service endpoints."""
from typing import Literal

from pydantic import BaseModel


class ReadinessResponse(BaseModel):
    """Response model used to indicate that the API is ready."""

    status: Literal["ready"] = "ready"