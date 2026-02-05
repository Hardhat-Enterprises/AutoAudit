"""Platform schemas for API responses."""

from pydantic import BaseModel, ConfigDict


class PlatformRead(BaseModel):
    """Schema for platform data."""

    id: int
    name: str
    display_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
