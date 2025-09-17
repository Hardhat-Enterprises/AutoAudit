import json, re, requests
from pathlib import Path

BASE = Path(__file__).resolve().parent
PARENT = BASE.parent
OPA = "http://127.0.0.1:8181"
PKG_RE = re.compile(r'^\s*package\s+([A-Za-z0-9_.]+)\s*$', re.MULTILINE)

def pkg_from_file(path: Path) -> str:
    m = PKG_RE.search(path.read_text(encoding="utf-8", errors="ignore"))
    if not m:
        raise ValueError(f"No 'package' line in {path}")
    return m.group(1)

requests.get(f"{OPA}/health", timeout=3).raise_for_status()

manifest = json.loads((BASE / "manifest.json").read_text())

reports, summary = [], {}

for group in manifest["groups"]:
    gid = group.get("id") or group.get("name", "unknown")
    cfg_path = (PARENT / group["config"]).resolve()
    input_data = json.loads(cfg_path.read_text())
    rego_paths = [(PARENT / p).resolve() for p in group["policies"]]

    gsum = summary.setdefault(gid, {"evaluated": 0, "errors": 0, "compliant": 0, "noncompliant": 0})

    for rego_path in rego_paths:
        pkg = pkg_from_file(rego_path)
        gsum["evaluated"] += 1

        try:
            r = requests.post(f"{OPA}/v1/data/{pkg}/report", json={"input": input_data}, timeout=10)
            r.raise_for_status()
            report = r.json().get("result")
        except Exception as e:
            gsum["errors"] += 1
            reports.append({
                "group": gid,
                "rego_file": str(rego_path),
                "package": pkg,
                "config": str(cfg_path),
                "error": str(e),
            })
            continue

        if not isinstance(report, dict):
            gsum["errors"] += 1
            reports.append({
                "group": gid,
                "rego_file": str(rego_path),
                "package": pkg,
                "config": str(cfg_path),
                "error": "report did not return an object",
                "raw": report,
            })
            continue

        status = report.get("status")
        if status == "Compliant":
            gsum["compliant"] += 1
        elif status == "NonCompliant":
            gsum["noncompliant"] += 1

        reports.append({
            "group": gid,
            "rego_file": str(rego_path),
            "package": pkg,
            "config": str(cfg_path),
            "report": report,
        })

out = PARENT / "autoaudit_reports.json"
out.write_text(json.dumps({"summary_by_group": summary, "reports": reports}, indent=2))
print(f"Wrote {out}")