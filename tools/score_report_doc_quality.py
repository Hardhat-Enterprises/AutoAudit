from pathlib import Path
import sys

SCORING_SECTIONS = {
    "## Purpose": 25,
    "## Starter Mapping": 25,
    "## Future Opportunities": 25,
    "## Conclusion": 25,
}


def calculate_score(file_path: Path) -> int:
    if not file_path.exists():
        print(f"Fail. File not found: {file_path}")
        return 0

    content = file_path.read_text(encoding="utf-8")
    lines = [
            line.strip().rstrip("#").strip()
            for line in content.splitlines()
            ]
    score = 0

    for section, points in SCORING_SECTIONS.items():
        if section in lines:
            score += points
            print(f"Pass. Found {section} (+{points})")
        else:
            print(f"Miss. Missing {section} (+0)")

    print(f"\nDocumentation Score: {score}/100")
    return score


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/score_report_doc_quality.py <markdown-file-path>")
        return 1

    score = calculate_score(Path(sys.argv[1]))

    return 0 if score == 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())