from pathlib import Path

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

POLICY_PATH = (
    ENGINE_ROOT
    / "policies"
    / "essential-eight"
    / "asd-essential-eight"
    / "v2025"
    / "e8_mfa_2_1_ca_enforcement.rego"
)

QUERY = (
    "data.essential_eight.asd_essential_eight.v2025."
    "control_e8_mfa_2_1.result"
)


def main() -> int:
    print("AutoAudit Compliance Engine Verification")
    print("=" * 40)
    print()

    passed = 0
    failed = 0

    for fixture_path in sorted(FIXTURE_DIR.glob("*.json")):
        try:
            fixture = load_fixture(fixture_path)

            result = run_policy(
                policy_path=POLICY_PATH,
                query=QUERY,
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

        except (FixtureError, OPAExecutionError) as exc:
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
