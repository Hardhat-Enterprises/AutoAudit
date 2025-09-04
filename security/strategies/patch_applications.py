from .overview import Strategy

class PatchApplications(Strategy):
    id = "PA"
    name = "Patch Applications"
    def description(self) -> str:
        return "To be described"