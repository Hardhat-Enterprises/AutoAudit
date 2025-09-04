import pkgutil, importlib, inspect
from .overview import Strategy

# load all the modules in the strategies and return them as a list 
def load_strategies():
    strategies = []
    pkg = __name__  

    # iterate the modules
    for _, modname, ispkg in pkgutil.iter_modules(__path__): 
        if ispkg or modname == "overview": # ignore the init.py and overview.py file 
            continue
        module = importlib.import_module(f"{pkg}.{modname}")

        # inspect the module for classes that inherit Strategy
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Strategy) and obj is not Strategy:
                strategies.append(obj())

    # to sort the strategies and return them as the list
    strategies.sort(key=lambda s: s.name.lower())
    return strategies