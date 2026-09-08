from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Starter Mapping",
    "## Future Opportunities",
    "## Conclusion",
]


def check_required_sections(file_path: Path) -> bool:
    if not file_path.exists():
        print(f"Fail. File not found: {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")
    lines = {line.strip() for line in content.splitlines()}

    missing_sections = [
        section for section in REQUIRED_SECTIONS if section not in lines
    ]

    if missing_sections:
        print("Fail. Missing required sections:")
        for section in missing_sections:
            print(f"- {section}")
        return False

    print("Pass. Documentation contains all required sections.")
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/check_report_doc_quality.py <markdown-file-path>")
        return 1

    return 0 if check_required_sections(Path(sys.argv[1])) else 1


if __name__ == "__main__":
    raise SystemExit(main())