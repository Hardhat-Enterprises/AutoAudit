from pathlib import Path
from security.strategies.regular_backups import get_strategy


EVID_DIR = Path("security/evidence/regular_backups")


def _short(hit):
    return f"{hit['test_id']} {hit['pass_fail']}"


def main():
    strat = get_strategy()

    if not EVID_DIR.exists():
        raise SystemExit(f"Evidence directory not found: {EVID_DIR.resolve()}")

    files = sorted(EVID_DIR.glob("*.txt"))
    if not files:
        raise SystemExit("No .txt evidence files found.")

    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        hits = strat.emit_hits(text, str(f))

        print(f"\n=== {f.as_posix()} ===")
        for h in hits:
            print(_short(h))

        # Rule 1: Never blank
        assert len(hits) > 0, f"{f.name} produced NO HITS"

        # Rule 2: ML2 files must include both ML1 and ML2 rows
        is_ml2 = "_ml2" in f.name.lower()
        if is_ml2:
            levels = {h["detected_level"] for h in hits}
            assert "ML1" in levels, f"{f.name} is ML2 but did not include ML1 hits"
            assert "ML2" in levels, f"{f.name} is ML2 but did not include ML2 hits"
        else:
            # ML1 files must not include ML2 rows
            levels = {h["detected_level"] for h in hits}
            assert "ML2" not in levels, f"{f.name} is ML1 but triggered ML2"

    print("\nALL TESTS PASSED ✅")


if __name__ == "__main__":
    main()