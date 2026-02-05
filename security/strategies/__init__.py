from __future__ import annotations

import importlib
from typing import List, Any

from .custom_benchmarks import get_strategy as get_benchmark_strategies

ESSENTIAL_EIGHT_MODULES = [
    "application_control",
    "restrict_admin_privileges",
    "patch_applications",
    "patch_operating_systems",
    "configure_macro_settings",
    "multi_factor_authentication",
    "regular_backups",
    "user_application_hardening",
]

FUNC_CANDIDATES = [
    "get_strategy",
    "get_strategies",
    "build_strategy",
    "strategy",
]

def _load_one(module_name: str):
    mod = importlib.import_module(f"{__name__}.{module_name}")

    for fn_name in FUNC_CANDIDATES:
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            obj = fn()
            return obj

    raise ImportError(
        f"{module_name}.py does not define any of: {', '.join(FUNC_CANDIDATES)}"
    )

def load_strategies() -> List[Any]:
    strategies: List[Any] = []

    try:
        strategies.extend(get_benchmark_strategies())
    except Exception:
        pass

    for m in ESSENTIAL_EIGHT_MODULES:
        try:
            s = _load_one(m)
            if isinstance(s, list):
                strategies.extend(s)
            else:
                strategies.append(s)
        except Exception:
            continue

    return strategies

def get_checker(strategy_name: str):
    return next((s for s in load_strategies() if getattr(s, "name", "") == strategy_name), None)

##