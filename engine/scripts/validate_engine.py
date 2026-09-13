from pathlib import Path

from validation.discovery import DiscoveryError, discover_controls
from validation.fixtures import (
    FixtureError, 
    discover_fixtures,
    load_fixture,
)
from validation.opa_runner import OPAExecutionError, run_policy
from validation.validator import (
    ResultContractError,
    validate_result_contract,
)
from validation.coverage import calculate_behavioral_coverage


ENGINE_ROOT = Path(__file__).resolve().parents[1]

FIXTURES_ROOT = (
    ENGINE_ROOT
    / "tests"
    / "fixtures"
    / "compliance"
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

    try:
        fixture_paths = discover_fixtures(FIXTURES_ROOT)
    except FixtureError as exc:
        print(f"Fixture discovery failed: {exc}")
        return 1

    passed = 0
    failed = 0
    tested_control_keys = set()

    for fixture_path in fixture_paths:
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

            tested_control_keys.add(key)

            control = controls[key]

            result = run_policy(
                policy_path=control.policy_path,
                query=control.query,
                input_data=fixture["input"],
            )

            validate_result_contract(result)

            expected = fixture["expected"]["compliant"]
            actual = result["compliant"]

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

        except (
            FixtureError, 
            DiscoveryError, 
            OPAExecutionError,
            ResultContractError,
        ) as exc:
            print(f"ERROR {fixture_path.name}")
            print(f"      {exc}")
            failed += 1

        coverage = calculate_behavioral_coverage(
            controls,
            tested_control_keys,
        )

    print()
    print(f"Fixtures executed: {passed + failed}")
    print(f"Passed:            {passed}")
    print(f"Failed:            {failed}")
    print()
    print(f"Ready automated controls:   {coverage.ready_controls}")
    print(f"Behaviour-tested controls:  {coverage.tested_controls}")
    print(
        f"Behavioural coverage:        "
        f"{coverage.coverage_percent:.1f}%"
    )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
