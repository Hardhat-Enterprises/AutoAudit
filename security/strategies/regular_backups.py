from .overview import Strategy

class RegularBackups(Strategy):
    id = "MFA"
    name = "Regular Backups"
    def description(self) -> str:
        return "To be described"