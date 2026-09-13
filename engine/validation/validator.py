class ResultContractError(Exception):
    """Raised when a policy result does not follow the expected contract."""


def validate_result_contract(result: object) -> None:
    """
    Validate the standard result structure returned by an AutoAudit policy.

    Required contract:
        compliant -> bool
        message   -> str
        details   -> dict
    """

    if not isinstance(result, dict):
        raise ResultContractError(
            "Policy result must be a JSON object"
        )

    required_fields = {
        "compliant",
        "message",
        "details",
    }

    missing = required_fields - result.keys()

    if missing:
        raise ResultContractError(
            "Policy result missing required field(s): "
            f"{', '.join(sorted(missing))}"
        )

    if not isinstance(result["compliant"], bool):
        raise ResultContractError(
            "Policy result field 'compliant' must be a boolean"
        )

    if not isinstance(result["message"], str):
        raise ResultContractError(
            "Policy result field 'message' must be a string"
        )

    if not isinstance(result["details"], dict):
        raise ResultContractError(
            "Policy result field 'details' must be an object"
        )