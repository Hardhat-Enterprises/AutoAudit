import json
import shutil
import subprocess
from pathlib import Path


class OPAExecutionError(Exception):
    """Raised when OPA cannot execute a policy successfully."""


def run_policy(
    policy_path: Path,
    query: str,
    input_data: dict,
) -> dict:
    """Execute a Rego policy through OPA and return its result."""

    opa_binary = shutil.which("opa")

    if opa_binary is None:
        raise OPAExecutionError(
            "OPA executable was not found on PATH"
        )

    command = [
        opa_binary,
        "eval",
        "--format=json",
        "--data",
        str(policy_path),
        "--stdin-input",
        query,
    ]

    process = subprocess.run(
        command,
        input=json.dumps(input_data),
        text=True,
        capture_output=True,
    )

    if process.returncode != 0:
        raise OPAExecutionError(
            f"OPA evaluation failed:\n{process.stderr}"
        )

    try:
        response = json.loads(process.stdout)

        return response["result"][0]["expressions"][0]["value"]

    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        raise OPAExecutionError(
            "OPA returned an unexpected result structure"
        ) from exc
