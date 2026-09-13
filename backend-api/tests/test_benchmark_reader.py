"""Unit tests for BenchmarkFileReader (filesystem, no HTTP)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.benchmark_reader import BenchmarkFileReader, get_file_reader


def _write_metadata(
    root: Path, framework: str, slug: str, version: str, payload: dict
) -> Path:
    version_dir = root / framework / slug / version
    version_dir.mkdir(parents=True)
    path = version_dir / "metadata.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


SAMPLE = {
    "framework": "cis",
    "slug": "microsoft-365-foundations",
    "version": "v3.1.0",
    "benchmark": "CIS M365",
    "controls": [
        {"control_id": "CIS-1.1.1", "title": "Ensure MFA"},
        {"control_id": "CIS-1.1.2", "title": "Legacy auth"},
    ],
}


def test_get_benchmark_path(tmp_path: Path) -> None:
    reader = BenchmarkFileReader(tmp_path)
    path = reader.get_benchmark_path("cis", "microsoft-365-foundations", "v3.1.0")
    assert path == tmp_path / "cis" / "microsoft-365-foundations" / "v3.1.0"


def test_get_benchmark_metadata_ok(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    reader = BenchmarkFileReader(tmp_path)
    meta = reader.get_benchmark_metadata("cis", "microsoft-365-foundations", "v3.1.0")
    assert meta["slug"] == "microsoft-365-foundations"
    assert len(meta["controls"]) == 2


def test_get_benchmark_metadata_missing(tmp_path: Path) -> None:
    reader = BenchmarkFileReader(tmp_path)
    with pytest.raises(FileNotFoundError):
        reader.get_benchmark_metadata("cis", "missing", "v1.0.0")


def test_get_control_metadata_ok(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    reader = BenchmarkFileReader(tmp_path)
    control = reader.get_control_metadata(
        "cis", "microsoft-365-foundations", "v3.1.0", "CIS-1.1.2"
    )
    assert control["title"] == "Legacy auth"


def test_get_control_metadata_not_found(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    reader = BenchmarkFileReader(tmp_path)
    with pytest.raises(ValueError, match="CIS-9.9.9"):
        reader.get_control_metadata(
            "cis", "microsoft-365-foundations", "v3.1.0", "CIS-9.9.9"
        )


def test_list_benchmarks_empty_dir(tmp_path: Path) -> None:
    reader = BenchmarkFileReader(tmp_path / "does-not-exist")
    assert reader.list_benchmarks() == []


def test_list_benchmarks_skips_junk(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    # Non-directories at each nesting level should be skipped.
    (tmp_path / "root-file.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "cis" / "readme.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "cis" / "microsoft-365-foundations" / "notes.txt").write_text(
        "ignore", encoding="utf-8"
    )
    # Version dir without metadata.json is skipped (not an error).
    (tmp_path / "cis" / "microsoft-365-foundations" / "v0.0.1").mkdir()
    bad = tmp_path / "cis" / "broken" / "v1.0.0"
    bad.mkdir(parents=True)
    (bad / "metadata.json").write_text("{not-json", encoding="utf-8")

    reader = BenchmarkFileReader(tmp_path)
    listed = reader.list_benchmarks()
    assert len(listed) == 1
    assert listed[0]["version"] == "v3.1.0"


def test_list_controls(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    reader = BenchmarkFileReader(tmp_path)
    controls = reader.list_controls("cis", "microsoft-365-foundations", "v3.1.0")
    assert [c["control_id"] for c in controls] == ["CIS-1.1.1", "CIS-1.1.2"]


def test_benchmark_exists(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "cis", "microsoft-365-foundations", "v3.1.0", SAMPLE)
    reader = BenchmarkFileReader(tmp_path)
    assert reader.benchmark_exists("cis", "microsoft-365-foundations", "v3.1.0") is True
    assert (
        reader.benchmark_exists("cis", "microsoft-365-foundations", "v9.9.9") is False
    )


def test_init_uses_settings_when_dir_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class _Settings:
        POLICIES_DIR = str(tmp_path)

    monkeypatch.setattr(
        "app.services.benchmark_reader.get_settings",
        lambda: _Settings(),
    )
    reader = BenchmarkFileReader()
    assert reader.policies_dir == tmp_path


def test_get_file_reader_cached(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    get_file_reader.cache_clear()
    monkeypatch.setattr(
        "app.services.benchmark_reader.BenchmarkFileReader",
        lambda: BenchmarkFileReader(tmp_path),
    )
    first = get_file_reader()
    second = get_file_reader()
    assert first is second
    get_file_reader.cache_clear()
