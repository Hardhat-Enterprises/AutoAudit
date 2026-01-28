import os
import subprocess
from pathlib import Path

# directory of results into one single folder
def ensure_results_dirs(root: Path) -> dict[str, Path]:
    results = root / "results"
    reports = results / "reports"
    previews = results / "previews"
    results.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    previews.mkdir(parents=True, exist_ok=True)
    return {
        "RESULTS_DIR": results,
        "REPORTS_DIR": reports,
        "PREVIEWS_DIR": previews,
        "CSV_PATH": results / "scan_report.csv",
        "TEMPLATE_PATH": results / "report_template.docx",
    }    

# Step 1: Welcome message
def main():
    print("=== Welcome to your dedicated Evidence Assistant ===")
    username = input("Enter your username: ").strip()
    if not username:
        username = "user"

    # Step 2: Choice of scan mode 
    print("\nPlease choose your preferred scan mode:")
    print("1. Scanner: batch scanning of evidences with CSV summary report")
    print("2. Report Generator: single evidence scan with pdf executive report generated")
    while True:
        choice = input("Pick 1 or 2: ").strip()
        if choice in {"1", "2"}:
            break
        print("Not a valid mode. Please try again.")

    # single results folder
    here = Path(__file__).resolve().parent
    paths = ensure_results_dirs(here)

    os.environ["AUTOAUDIT_USER"] = username
    os.environ["AUTOAUDIT_RESULTS"] = str(paths["RESULTS_DIR"])
    os.environ["AUTOAUDIT_REPORTS"] = str(paths["REPORTS_DIR"])
    os.environ["AUTOAUDIT_PREVIEWS"] = str(paths["PREVIEWS_DIR"])
    os.environ["AUTOAUDIT_CSV"] = str(paths["CSV_PATH"])
    os.environ["AUTOAUDIT_TEMPLATE"] = str(paths["TEMPLATE_PATH"])

    # Step 3: Run the respective python script 
    scanner = str((here / "evidence_backend" / "scanner.py").resolve())
    reportg = str((here / "evidence_backend" / "reportgenerator.py").resolve())

    if choice == "1":
        print("\n▶ Running scanner.py ...")
        here = Path(__file__).resolve().parent
        os.environ["AUTOAUDIT_INPUT_DIR"] = str(here / "evidence")
        subprocess.run(["python", scanner], check=False)
    else:
        print("\n▶ Running reportgenerator.py ...")
        here = Path(__file__).resolve().parent
        os.environ["AUTOAUDIT_INPUT_DIR"] = str(here / "evidence")
        subprocess.run(["python", reportg], check=False)

if __name__ == "__main__":
    main()