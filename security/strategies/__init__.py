import pkgutil, importlib, inspect
from .overview import Strategy

def load_strategies():
    strategies = []
    pkg = __name__

    # iterate over all modules in strategies
    for _, modname, ispkg in pkgutil.iter_modules(__path__):
        if ispkg or modname == "overview":
            continue
        module = importlib.import_module(f"{pkg}.{modname}")

        # prefer get_strategy() if present
        if hasattr(module, "get_strategy"):
            strategies.append(module.get_strategy())
            continue

        # otherwise find subclasses of Strategy
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Strategy) and obj is not Strategy:
                strategies.append(obj())

    # sort alphabetically
    strategies.sort(key=lambda s: s.name.lower())
    return strategies
