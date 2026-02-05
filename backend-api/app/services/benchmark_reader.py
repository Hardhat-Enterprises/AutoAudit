"""Read benchmark and control metadata from policy files at runtime.

Policies are organized as:
    policies/{framework}/{benchmark-slug}/{version}/metadata.json
    policies/{framework}/{benchmark-slug}/{version}/*.rego

Example:
    policies/cis/microsoft-365-foundations/v3.1.0/metadata.json
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class BenchmarkFileReader:
    """Read benchmark and control metadata from files at runtime."""

    def __init__(self, policies_dir: Path | str | None = None):
        if policies_dir is None:
            settings = get_settings()
            policies_dir = getattr(settings, "POLICIES_DIR", "/app/policies")
        self.policies_dir = Path(policies_dir)

    def get_benchmark_path(self, framework: str, slug: str, version: str) -> Path:
        """Get the path to a benchmark's directory."""
        return self.policies_dir / framework / slug / version

    def get_benchmark_metadata(self, framework: str, slug: str, version: str) -> dict[str, Any]:
        """Read metadata.json for a benchmark.

        Args:
            framework: e.g., "cis"
            slug: e.g., "microsoft-365-foundations"
            version: e.g., "v3.1.0"

        Returns:
            The full metadata dict including benchmark info and controls.

        Raises:
            FileNotFoundError: If metadata.json doesn't exist.
        """
        path = self.get_benchmark_path(framework, slug, version) / "metadata.json"
        if not path.exists():
            raise FileNotFoundError(f"Metadata not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def get_control_metadata(
        self, framework: str, slug: str, version: str, control_id: str
    ) -> dict[str, Any]:
        """Get control details from metadata.json.

        Args:
            framework: e.g., "cis"
            slug: e.g., "microsoft-365-foundations"
            version: e.g., "v3.1.0"
            control_id: e.g., "CIS-1.1.1"

        Returns:
            Control metadata dict.

        Raises:
            ValueError: If control is not found.
            FileNotFoundError: If metadata.json doesn't exist.
        """
        metadata = self.get_benchmark_metadata(framework, slug, version)
        for control in metadata.get("controls", []):
            if control.get("control_id") == control_id:
                return control
        raise ValueError(f"Control {control_id} not found in {framework}/{slug}/{version}")

    def list_benchmarks(self) -> list[dict[str, Any]]:
        """List all available benchmarks by scanning the policies directory.

        Returns:
            List of benchmark metadata dicts.
        """
        benchmarks = []
        if not self.policies_dir.exists():
            return benchmarks

        for framework_dir in self.policies_dir.iterdir():
            if not framework_dir.is_dir():
                continue
            for benchmark_dir in framework_dir.iterdir():
                if not benchmark_dir.is_dir():
                    continue
                for version_dir in benchmark_dir.iterdir():
                    if not version_dir.is_dir():
                        continue
                    metadata_file = version_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
                            benchmarks.append(metadata)
                        except (json.JSONDecodeError, OSError):
                            pass
        return benchmarks

    def list_controls(self, framework: str, slug: str, version: str) -> list[dict[str, Any]]:
        """List all controls for a specific benchmark.

        Returns:
            List of control metadata dicts.
        """
        metadata = self.get_benchmark_metadata(framework, slug, version)
        return metadata.get("controls", [])

    def benchmark_exists(self, framework: str, slug: str, version: str) -> bool:
        """Check if a benchmark exists on disk."""
        path = self.get_benchmark_path(framework, slug, version) / "metadata.json"
        return path.exists()


@lru_cache(maxsize=1)
def get_file_reader() -> BenchmarkFileReader:
    """Get a cached file reader instance."""
    return BenchmarkFileReader()
