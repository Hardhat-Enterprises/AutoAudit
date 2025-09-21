import json
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Locate current directory (same as aggregator.py)
HERE = Path(__file__).resolve().parent
JSON_FILE = HERE / "autoaudit_reports.json"
PDF_FILE = HERE / "autoaudit_report.pdf"

def main():
    # Load JSON report
    if not JSON_FILE.exists():
        print(f"JSON report not found at {JSON_FILE}")
        return

    data = json.loads(JSON_FILE.read_text())

    # PDF setup
    doc = SimpleDocTemplate(str(PDF_FILE), pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>AutoAudit Compliance Report</b>", styles['Title']))
    elements.append(Spacer(1, 20))

    for rule, details in data.items():
        elements.append(Paragraph(f"<b>{rule}</b>", styles['Heading2']))

        if "error" in details and details["error"]:
            elements.append(Paragraph(f"❌ Error: {details['error']}", styles['Normal']))
        else:
            elements.append(Paragraph(f"Title: {details.get('title','')}", styles['Normal']))
            elements.append(Paragraph(f"Status: {details.get('status','')}", styles['Normal']))
            elements.append(Paragraph(f"Group: {details.get('input_kind','')}", styles['Normal']))
            elements.append(Paragraph(f"Verification: {details.get('verification','')}", styles['Normal']))
            elements.append(Paragraph(f"Remediation: {details.get('remediation','')}", styles['Normal']))

            if details.get("violations"):
                elements.append(Paragraph("Violations:", styles['Italic']))
                for v in details["violations"]:
                    elements.append(Paragraph(f"- {v}", styles['Normal']))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    print(f"✅ PDF written to {PDF_FILE}")

if __name__ == "__main__":
    main()