from fastapi import APIRouter

from app.models.strategy import Strategy
from app.services.strategies import list_strategies


router = APIRouter(prefix="/strategies", tags=["Strategies"])


@router.get("/", response_model=list[Strategy])
def get_strategies() -> list[Strategy]:
    """
    Return all available strategies with metadata, so the UI can render
    names, descriptions, severity, and evidence type hints.
    """
    return list_strategies()
