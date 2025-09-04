from .overview import Strategy

class MultiFactorAuthentication(Strategy):
    id = "MFA"
    name = "Multi-Factor Authentication"
    def description(self) -> str:
        return "To be described"