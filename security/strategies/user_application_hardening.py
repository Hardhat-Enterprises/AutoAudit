from .overview import Strategy

class UserApplicationHardening(Strategy):
    id = "UAH"
    name = "User Application Hardening"
    def description(self) -> str:
        return "To be described"