"""Discover AutoAudit compliance controls and their associated Rego policies."""

import json
import re
from dataclasses import dataclass
from pathlib import Path


class DiscoveryError(Exception):
    """Raised when a compliance control or policy cannot be discovered."""

#pylint: disable=too-many-instance-attributes
@dataclass
class ControlDefinition:
    """Metadata required to loacte and execute a compliance control."""

    framework: str
    benchmark: str
    version: str
    control_id: str
    policy_path: Path
    package: str
    query: str
    metadata_path: Path
    automation_status: str | None
    benchmark_audit_type: str | None


def _walk_objects(value):
    """Yield every dictionary contained in a JSON structure."""

    if isinstance(value, dict):
        yield value

        for child in value.values():
            yield from _walk_objects(child)

    elif isinstance(value, list):
        for child in value:
            yield from _walk_objects(child)


def _read_rego_package(policy_path: Path) -> str:
    """Read the package declaration from a Rego policy."""

    content = policy_path.read_text(encoding="utf-8")

    match = re.search(
        r"^\s*package\s+([A-Za-z0-9_.]+)\s*$",
        content,
        re.MULTILINE,
    )

    if match is None:
        raise DiscoveryError(
            f"{policy_path}: no Rego package declaration found"
        )

    return match.group(1)


def discover_controls(
    policies_root: Path,
) -> dict[tuple[str, str, str, str], ControlDefinition]:
    """
    Discover controls from policy metadata and map them to
    their Rego policies and OPA result queries.
    """

    controls: dict[tuple[str, str, str, str], ControlDefinition] = {}

    for metadata_path in policies_root.rglob("metadata.json"):

        parts = metadata_path.parent.relative_to(policies_root).parts

        if len(parts) < 3:
            raise DiscoveryError(
                f"{metadata_path}: expected framework/benchmark/version directory structure"
            )

        framework, benchmark, version = parts[:3]

        try:
            metadata = json.loads(
                metadata_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            raise DiscoveryError(
                f"{metadata_path}: invalid JSON: {exc}"
            ) from exc

        for item in _walk_objects(metadata):
            control_id = item.get("control_id")
            policy_file = item.get("policy_file")

            if not control_id or not policy_file:
                continue

            key = (
                framework,
                benchmark,
                version,
                control_id,
            )

            if key in controls:
                raise DiscoveryError(
                    "Duplicate fully-qualified control discovered: "
                    f"{framework}/{benchmark}/{version}/{control_id}"
                )

            policy_path = metadata_path.parent / policy_file

            if not policy_path.is_file():
                raise DiscoveryError(
                    f"{control_id}: policy file does not exist: "
                    f"{policy_path}"
                )

            package = _read_rego_package(policy_path)

            controls[key] = ControlDefinition(
                framework=framework,
                benchmark=benchmark,
                version=version,
                control_id=control_id,
                policy_path=policy_path,
                package=package,
                query=f"data.{package}.result",
                metadata_path=metadata_path,
                automation_status=item.get("automation_status"),
                benchmark_audit_type=item.get("benchmark_audit_type"),
            )

    return controls
