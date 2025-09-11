# Evidence Assistant

This is your assistant that automatically scans, validates and organises evidences, or also known as screenshots, against the **Essential 8 Framework**. It aims to help users validate text evidence or screenshots (e.g. Windows environment) against the security strategies using OCR (Tesseract) and keyword rules to generate meaningful **PDF/CSV reports**. 

---

## Strategies Supported

1. Application Control 
2. Patch Applications 
3. Configure Microsoft Office Macro Settings  
4. User Application Hardening
5. Restrict Administrative Privileges
6. Patch Operating Systems
7. Multi-Factor Authentication
8. Regular Backups

---

## How It Works

- Provide evidences in common format like JPEG, PNG, PDF, DOCX or text files in the **evidence/** folder 
- The tool extracts visible text using **Tesseract OCR** and checks for non-compliance indicators using strategy-specific keyword rules
- Results are saved in the **results/** folder with reports generated in CSV or PDF depending on the mode chosen

---

## Set up and Requirements

- **Python 3.9+**  
  For running the Evidence Assistant and manage dependencies  
  [Download Python](https://www.python.org/downloads/)  

- **Tesseract OCR**  
  Required for extracting text from images/screenshots  
  Install via:  
  - macOS: `brew install tesseract`  
  - Ubuntu/Debian: `sudo apt install tesseract-ocr`  
  - Windows: [Download installer](https://github.com/tesseract-ocr/tesseract) and add the install folder (e.g., `C:\Program Files\Tesseract-OCR`) to your **System PATH**

---

## Running the Tool

After installing Python and Tesseract, there are two options to run the tool:

**Option 1: Command-Line Interface (CLI)**
- Set up the virtual environment, install all the requirements and run the program 
```
python -m venv .venv && source .venv/bin/activate # macOS/Linux
python -m venv .venv && .venv\Scripts\activate # Windows
pip install -r security/requirements.txt
python security/evidenceassistant.py
```
- The CLI provides two modes:
(1) Scanner mode: able to batch scan multiple files and generate a CSV summary 
(2) Report Generator mode: able to scan a single file at one time and generate a PDF executive report 

**Option 2: Web Interface (UI)**
- For a user-friendly interface, launch the web app and upload evidences directly using the browser
- Note: the UI only has the Report Generator mode for now 
```
python -m venv .venv && source .venv/bin/activate # macOS/Linux
python -m venv .venv && .venv\Scripts\activate # Windows
pip install -r security/requirements.txt
python -m uvicorn aa_ui:app --reload
```
---

## Folder Structure

AutoAudit/Security/
├── aa_ui/             # Web UI files and name to be changed to "frontend" 
│   ├── ui.html
│   └── ui.py
├── backend/              # Core OCR + scanner/reportgenerator tools
│   ├── core_ocr.py
│   ├── scanner.py
│   ├── reportgenerator.py
├── evidence/             # Place your screenshots/docs here
├── reports/              # Report generation logic
├── results/              # Auto-generated reports and preview documents
│   ├── scan_report.csv
│   ├── reports/
│   └── previews/
├── strategies/           # Detection rules per strategy
├── requirements.txt      # Python dependencies
└── evidenceassistant.py  # CLI wrapper

---

## Next Steps

**Recommendations**
1. Improve reportgenerator.py so that one screenshot = one consolidated report (with all test IDs inside) >> "Screenshot1 AC-01 03 04" can be used for testing 
2. Refactor the UI code to directly adopt scanner.py and reportgenerator.py from backend/, instead of duplicating logic, to reduce maintenance overhead and avoid inconsistencies
