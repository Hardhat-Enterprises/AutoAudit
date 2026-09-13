from pathlib import Path

from validation.discovery import DiscoveryError, discover_controls
from validation.fixtures import FixtureError, load_fixture
from validation.opa_runner import OPAExecutionError, run_policy


ENGINE_ROOT = Path(__file__).resolve().parents[1]

FIXTURE_DIR = (
    ENGINE_ROOT
    / "tests"
    / "fixtures"
    / "compliance"
    / "e8_mfa_2_1"
)

def main() -> int:
    print("AutoAudit Compliance Engine Verification")
    print("=" * 40)
    print()

    try: 
        controls = discover_controls(ENGINE_ROOT / "policies")
    except DiscoveryError as exc:
        print(f"Discovery failed: {exc}")
        return 1

    passed = 0
    failed = 0

    for fixture_path in sorted(FIXTURE_DIR.glob("*.json")):
        try:
            fixture = load_fixture(fixture_path)

            key = (
                fixture["framework"],
                fixture["benchmark"],
                fixture["version"],
                fixture["control_id"],
            )

            if key not in controls:
                raise DiscoveryError(
                    "No policy metadata found for "
                    f"{'/'.join(key)}"
                )

            control = controls[key]

            result = run_policy(
                policy_path=control.policy_path,
                query=control.query,
                input_data=fixture["input"],
            )

            expected = fixture["expected"]["compliant"]
            actual = result.get("compliant")

            if actual == expected:
                print(
                    f"PASS  {fixture['control_id']} - "
                    f"{fixture['scenario']}"
                )
                passed += 1

            else:
                print(
                    f"FAIL  {fixture['control_id']} - "
                    f"{fixture['scenario']}"
                )
                print(f"      Expected compliant: {expected}")
                print(f"      Actual compliant:   {actual}")
                failed += 1

        except (FixtureError, DiscoveryError, OPAExecutionError) as exc:
            print(f"ERROR {fixture_path.name}")
            print(f"      {exc}")
            failed += 1

    print()
    print(f"Fixtures executed: {passed + failed}")
    print(f"Passed:            {passed}")
    print(f"Failed:            {failed}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
