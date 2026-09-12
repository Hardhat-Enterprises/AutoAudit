"""Every policy's `# METADATA` service must agree with `metadata.json`.

The annotation in the policy source and the record in `metadata.json` name the
same thing twice, and nothing made them agree. This file is the gate that keeps
them agreeing, across every benchmark in the tree.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
POLICIES = ENGINE_ROOT / "policies"


def test_the_rego_annotation_agrees_with_the_benchmark_metadata():
    """A control described two ways is described wrong in one of them.

    Every policy carries a `# METADATA` block naming the service it assesses,
    and `metadata.json` names it again. Thirteen controls disagreed -- the whole
    of CIS section 2.1 plus 2.4.4, annotated `Exchange` while the metadata said
    `Defender`. metadata.json is what the UI, the documentation generator and
    the crosswalk all read, so the annotation was the copy that had drifted, and
    a reader of the policy source was told something different from a reader of
    the product.
    """
    mismatched: list[str] = []
    for metadata_path in sorted(POLICIES.glob("*/*/*/metadata.json")):
        if "candidate" in metadata_path.parts:
            continue
        metadata = json.loads(metadata_path.read_text())
        for control in metadata["controls"]:
            policy_file = control.get("policy_file")
            if not policy_file:
                continue
            source = (metadata_path.parent / policy_file).read_text()
            annotated = re.search(r"^#\s+service:\s*(\S+)\s*$", source, re.MULTILINE)
            if annotated is None:
                continue
            if annotated.group(1) != control.get("service"):
                mismatched.append(
                    f"{policy_file}: annotated {annotated.group(1)!r}, "
                    f"metadata.json says {control.get('service')!r}"
                )
    assert not mismatched, "\n  ".join(["service annotations disagree:", *mismatched])
