import json
from pathlib import Path


class FixtureError(Exception):
    """Raised when a compliance verification fixture is invalid."""


def load_fixture(path: Path) -> dict:
    """Load and perform basic validation of a compliance fixture."""

    try:
        with path.open("r", encoding="utf-8") as file:
            fixture = json.load(file)
    except json.JSONDecodeError as exc:
        raise FixtureError(f"{path}: invalid JSON: {exc}") from exc

    required_fields = {"control_id", "scenario", "input", "expected"}

    missing = required_fields - fixture.keys()

    if missing:
        raise FixtureError(
            f"{path}: missing required field(s): {', '.join(sorted(missing))}"
        )

    if not isinstance(fixture["input"], dict):
        raise FixtureError(f"{path}: 'input' must be a JSON object")

    if not isinstance(fixture["expected"], dict):
        raise FixtureError(f"{path}: 'expected' must be a JSON object")

    if "compliant" not in fixture["expected"]:
        raise FixtureError(
            f"{path}: expected result must define 'compliant'"
        )

    if not isinstance(fixture["expected"]["compliant"], bool):
        raise FixtureError(
            f"{path}: expected.compliant must be true or false"
        )

    return fixture