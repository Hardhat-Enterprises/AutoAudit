from __future__ import annotations
import json, os
from datetime import datetime
from pathlib import Path

# Always anchor to the repo root: ...\security
BASE_DIR    = Path(__file__).resolve().parents[2]  # backend/logging -> backend -> security
RESULTS_DIR = Path(os.environ.get("AUTOAUDIT_RESULTS", BASE_DIR / "results"))
LOG_PATH    = RESULTS_DIR / "scan_log.jsonl"

def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()

def write_scan_log(*, user: str, strategy: str, status: str) -> None:
    """Append one record to scan_log.jsonl with minimal fields."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    row = {"ts": _now_iso(), "user": user, "strategy": strategy, "status": status}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

# Optional quick check: run `py backend\logging\scan_logger.py`
if __name__ == "__main__":
    print("LOG_PATH ->", LOG_PATH)
