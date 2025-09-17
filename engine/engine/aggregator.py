import json, subprocess, re, sys
from pathlib import Path

THIS = Path(__file__).resolve()

ROOT = next(p for p in [THIS.parent, *THIS.parents] if (p / "rules").exists() and (p / "test-configs").exists())

RULES = ROOT / "rules"
CONFIGS = ROOT / "test-configs"
OUTFILE = ROOT / "autoaudit_reports.json"

EXTRA_DATA_DIRS: list[str] = []

PKG_RE = re.compile(r'^\s*package\s+([A-Za-z0-9_.]+)\s*$', re.MULTILINE)

def pkg_from_file(path: Path) -> str:
    m = PKG_RE.search(path.read_text(encoding="utf-8", errors="ignore"))
    if not m:
        raise ValueError(f"No 'package' in {path}")
    return m.group(1)

def opa_eval(rego_path: Path, input_path: Path, query: str) -> dict:
    """Run `opa eval -f json -d RULES [-d EXTRA...] -i input query` and return parsed JSON."""
    cmd = ["opa", "eval", "-f", "json", "-d", str(RULES)]
    for d in EXTRA_DATA_DIRS:
        cmd += ["-d", d]
    cmd += ["-i", str(input_path), query]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"opa eval failed for {rego_path}")
    try:
        return json.loads(proc.stdout)
    except Exception as e:
        raise RuntimeError(f"Invalid JSON from opa eval: {e}")

def extract_value_from_eval(eval_json: dict):
    """Return the expression value (or None)."""
    res = eval_json.get("result") or []
    if not res:
        return None
    exprs = res[0].get("expressions") or []
    if not exprs:
        return None
    return exprs[0].get("value")

def main():
    manifest_path = THIS.parent / "manifest.json"
    if not manifest_path.exists():
        print(f"Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(2)

    manifest = json.loads(manifest_path.read_text())
    groups = manifest.get("groups")
    if not isinstance(groups, list):
        print("manifest.json must contain an array field 'groups'", file=sys.stderr)
        sys.exit(2)

    reports = []
    summary = {}

    for group in groups:
        gid = group.get("id") or group.get("name", "unknown")
        policies = group.get("policies") or []
        config_name = group.get("config")
        if not policies or not config_name:
            print(f"Skipping group {gid}: missing 'policies' or 'config'", file=sys.stderr)
            continue

        input_path = (CONFIGS / config_name).resolve()
        gsum = summary.setdefault(gid, {"evaluated": 0, "errors": 0, "compliant": 0, "noncompliant": 0})

        for pol in policies:
            rego_path = (RULES / pol).resolve()
            if not rego_path.exists():
                gsum["errors"] += 1
                reports.append({
                    "group": gid, "rego_file": str(rego_path), "config": str(input_path),
                    "error": "rego file not found"
                })
                continue

            pkg = pkg_from_file(rego_path)
            query = f"data.{pkg}.report"
            gsum["evaluated"] += 1

            try:
                ej = opa_eval(rego_path, input_path, query)
                value = extract_value_from_eval(ej)
            except Exception as e:
                gsum["errors"] += 1
                reports.append({
                    "group": gid, "rego_file": str(rego_path), "package": pkg,
                    "config": str(input_path), "error": str(e)
                })
                continue

            if not isinstance(value, dict):
                # Helpful: dump available keys at the package root to debug
                try:
                    ej2 = opa_eval(rego_path, input_path, f"data.{pkg}")
                    pkg_root = extract_value_from_eval(ej2)
                    available_keys = list(pkg_root.keys()) if isinstance(pkg_root, dict) else None
                except Exception:
                    available_keys = None

                gsum["errors"] += 1
                reports.append({
                    "group": gid, "rego_file": str(rego_path), "package": pkg,
                    "config": str(input_path), "error": "report returned null or non-object",
                    "available_keys": available_keys
                })
                continue

            status = value.get("status")
            if status == "Compliant":
                gsum["compliant"] += 1
            elif status == "NonCompliant":
                gsum["noncompliant"] += 1

            reports.append({
                "group": gid, "rego_file": str(rego_path), "package": pkg,
                "config": str(input_path), "report": value
            })

    OUTFILE.write_text(json.dumps({"summary_by_group": summary, "reports": reports}, indent=2))
    print(f"Wrote {OUTFILE}")

if __name__ == "__main__":
    main()