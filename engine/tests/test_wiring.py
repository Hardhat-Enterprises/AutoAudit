"""Structural consistency checks between metadata, rego policies, and the collector registry.

These tests run in CI on every PR to catch wiring mistakes -- mismatched
references between the three artifacts that must stay in sync:
  1. metadata.json  (control definitions)
  2. *.rego files   (OPA policy code)
  3. DATA_COLLECTORS registry  (Python collector classes)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

ENGINE_ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = ENGINE_ROOT / "policies"

VALID_AUTOMATION_STATUSES = {"ready", "manual", "deferred", "blocked", "not_started"}

# ---------------------------------------------------------------------------
# Metadata discovery
# ---------------------------------------------------------------------------


def _load_all_metadata() -> list[tuple[Path, dict]]:
    """Return (path, parsed_json) for every metadata.json under the policies tree."""
    result = []
    for p in sorted(POLICIES_DIR.rglob("metadata.json")):
        with open(p, encoding="utf-8") as f:
            result.append((p, json.load(f)))
    return result


_ALL_METADATA: list[tuple[Path, dict]] = _load_all_metadata()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PACKAGE_RE = re.compile(r"^package\s+(\S+)", re.MULTILINE)


def _expected_package(framework: str, slug: str, version: str, control_id: str) -> str:
    """Replicate the package-path logic from worker/tasks.py:380-395."""
    benchmark_normalized = slug.replace("-", "_")
    version_normalized = version.replace(".", "_")
    control_suffix = control_id.replace(".", "_")
    return f"{framework}.{benchmark_normalized}.{version_normalized}.control_{control_suffix}"


def _extract_rego_package(rego_path: Path) -> str | None:
    """Read a .rego file and return its package declaration, or None."""
    text = rego_path.read_text(encoding="utf-8")
    m = _PACKAGE_RE.search(text)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Parametrize data builders
# ---------------------------------------------------------------------------


def _ready_controls() -> list[tuple[str, str, dict, Path, dict]]:
    """(version_label, control_id, control, version_dir, meta) for ready controls."""
    items = []
    for meta_path, meta in _ALL_METADATA:
        version_dir = meta_path.parent
        version_label = f"{meta['slug']}/{meta['version']}"
        for ctrl in meta["controls"]:
            if ctrl["automation_status"] == "ready":
                items.append((version_label, ctrl["control_id"], ctrl, version_dir, meta))
    return items


def _ready_controls_with_policy() -> list[tuple[str, str, dict, Path, dict]]:
    """Same as _ready_controls but only those with a non-null policy_file."""
    return [t for t in _ready_controls() if t[2]["policy_file"] is not None]


def _all_rego_files() -> list[tuple[str, str, Path]]:
    """(version_label, filename, path) for every .rego file on disk."""
    items = []
    for meta_path, meta in _ALL_METADATA:
        version_dir = meta_path.parent
        version_label = f"{meta['slug']}/{meta['version']}"
        for rego in sorted(version_dir.glob("*.rego")):
            items.append((version_label, rego.name, rego))
    return items


def _all_controls() -> list[tuple[str, str, dict]]:
    """(version_label, control_id, control) for ALL controls."""
    items = []
    for meta_path, meta in _ALL_METADATA:
        version_label = f"{meta['slug']}/{meta['version']}"
        for ctrl in meta["controls"]:
            items.append((version_label, ctrl["control_id"], ctrl))
    return items


def _all_metadata_collector_ids() -> set[str]:
    """All collector IDs referenced across every metadata.json."""
    ids: set[str] = set()
    for _, meta in _ALL_METADATA:
        for c in meta["controls"]:
            if c["data_collector_id"]:
                ids.add(c["data_collector_id"])
    return ids


def _orphaned_collectors() -> list[str]:
    from collectors.registry import DATA_COLLECTORS

    referenced = _all_metadata_collector_ids()
    return sorted(cid for cid in DATA_COLLECTORS if cid not in referenced)


# Pre-compute parametrize data and IDs
_READY = _ready_controls()
_READY_IDS = [f"{v}-{cid}" for v, cid, _, _, _ in _READY]

_READY_WITH_POLICY = _ready_controls_with_policy()
_READY_WITH_POLICY_IDS = [f"{v}-{cid}" for v, cid, _, _, _ in _READY_WITH_POLICY]

_REGO_FILES = _all_rego_files()
_REGO_FILES_IDS = [f"{v}-{fname}" for v, fname, _ in _REGO_FILES]

_ALL_CONTROLS = _all_controls()
_ALL_CONTROLS_IDS = [f"{v}-{cid}" for v, cid, _ in _ALL_CONTROLS]

_ORPHANED = _orphaned_collectors()


# ---------------------------------------------------------------------------
# Test 1: Every ready control's policy_file exists on disk
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version_label,control_id,control,version_dir,meta",
    _READY,
    ids=_READY_IDS,
)
def test_ready_control_policy_file_exists(version_label, control_id, control, version_dir, meta):
    policy_file = control["policy_file"]
    assert policy_file is not None, (
        f"[{version_label}] control {control_id} has automation_status='ready' "
        f"but policy_file is null"
    )
    rego_path = version_dir / policy_file
    assert rego_path.is_file(), (
        f"[{version_label}] control {control_id} references policy_file='{policy_file}' "
        f"but file does not exist at {rego_path}"
    )


# ---------------------------------------------------------------------------
# Test 2: Every ready control's data_collector_id is registered
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version_label,control_id,control,version_dir,meta",
    _READY,
    ids=_READY_IDS,
)
def test_ready_control_collector_registered(version_label, control_id, control, version_dir, meta):
    from collectors.registry import DATA_COLLECTORS

    collector_id = control["data_collector_id"]
    assert collector_id is not None, (
        f"[{version_label}] control {control_id} has automation_status='ready' "
        f"but data_collector_id is null"
    )
    assert collector_id in DATA_COLLECTORS, (
        f"[{version_label}] control {control_id} references collector '{collector_id}' "
        f"which is not registered in DATA_COLLECTORS"
    )


# ---------------------------------------------------------------------------
# Test 3: Rego package declaration matches expected path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version_label,control_id,control,version_dir,meta",
    _READY_WITH_POLICY,
    ids=_READY_WITH_POLICY_IDS,
)
def test_rego_package_matches_metadata(version_label, control_id, control, version_dir, meta):
    rego_path = version_dir / control["policy_file"]
    if not rego_path.is_file():
        pytest.skip("Rego file missing (covered by test_ready_control_policy_file_exists)")

    actual_package = _extract_rego_package(rego_path)
    assert actual_package is not None, (
        f"[{version_label}] {control['policy_file']} has no 'package' declaration"
    )

    expected = _expected_package(
        framework=meta["framework"],
        slug=meta["slug"],
        version=meta["version"],
        control_id=control_id,
    )
    assert actual_package == expected, (
        f"[{version_label}] {control['policy_file']} declares package '{actual_package}' "
        f"but expected '{expected}'"
    )


# ---------------------------------------------------------------------------
# Test 4: No orphaned rego files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version_label,filename,rego_path",
    _REGO_FILES,
    ids=_REGO_FILES_IDS,
)
def test_no_orphaned_rego_files(version_label, filename, rego_path):
    meta_path = rego_path.parent / "metadata.json"
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    referenced_files = {c["policy_file"] for c in meta["controls"] if c["policy_file"]}
    assert filename in referenced_files, (
        f"[{version_label}] Rego file '{filename}' exists on disk but is not referenced "
        f"by any control in metadata.json"
    )


# ---------------------------------------------------------------------------
# Test 5: No orphaned collectors
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("collector_id", _ORPHANED)
def test_no_orphaned_collectors(collector_id):
    pytest.fail(
        f"Collector '{collector_id}' is registered in DATA_COLLECTORS but not referenced "
        f"by any control in any metadata.json"
    )


# ---------------------------------------------------------------------------
# Test 6: Schema consistency per control
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version_label,control_id,control",
    _ALL_CONTROLS,
    ids=_ALL_CONTROLS_IDS,
)
def test_control_schema_consistency(version_label, control_id, control):
    status = control["automation_status"]
    assert status in VALID_AUTOMATION_STATUSES, (
        f"[{version_label}] control {control_id} has invalid "
        f"automation_status='{status}'. Valid: {VALID_AUTOMATION_STATUSES}"
    )

    if status == "ready":
        assert control["data_collector_id"] is not None, (
            f"[{version_label}] control {control_id} is 'ready' but data_collector_id is null"
        )
        assert control["policy_file"] is not None, (
            f"[{version_label}] control {control_id} is 'ready' but policy_file is null"
        )
    else:
        assert control["policy_file"] is None, (
            f"[{version_label}] control {control_id} has automation_status='{status}' "
            f"but policy_file='{control['policy_file']}' is not null"
        )


# ---------------------------------------------------------------------------
# Test 7: No duplicate control_ids within a version
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "meta_path,meta",
    _ALL_METADATA,
    ids=[meta["version"] for _, meta in _ALL_METADATA],
)
def test_no_duplicate_control_ids(meta_path, meta):
    ids = [c["control_id"] for c in meta["controls"]]
    seen: dict[str, int] = {}
    for cid in ids:
        seen[cid] = seen.get(cid, 0) + 1
    duplicates = {cid: count for cid, count in seen.items() if count > 1}
    assert not duplicates, (
        f"[{meta['slug']}/{meta['version']}] Duplicate control_ids: {duplicates}"
    )
