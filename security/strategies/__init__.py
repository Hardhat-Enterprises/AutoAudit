from .custom_benchmarks import get_strategy, STRATEGY_DEFS

# Canonical set of strategies the UI should see (order preserved)
ALLOWED_STRATEGIES = {entry["name"]: entry["description"] for entry in STRATEGY_DEFS}


def load_strategies():
    """Return the curated strategies with embedded rule logic."""
    return list(get_strategy())


def get_checker(strategy_name: str):
    """Return the strategy object by name (or None)."""
    return next((s for s in load_strategies() if s.name == strategy_name), None)
