"""Pydantic schema for a validator match item."""

from pydantic import BaseModel


class ValidatorMatch(BaseModel):
    """A single matched term with occurrence count."""

    term: str
    count: int


