import json
import sys
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
JSON_FILE = HERE / "autoaudit_reports.json"
PDF_FILE = HERE / "autoaudit_report.pdf"

def main() -> None:
    if not JSON_FILE.exists():
        print(f"JSON report not found at {JSON_FILE}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(JSON_FILE.read_text())

    doc = SimpleDocTemplate(str(PDF_FILE), pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>AutoAudit Compliance Report</b>", styles['Title']))
    elements.append(Spacer(1, 20))

    for rule, details in data.items():
        elements.append(Paragraph(f"<b>{rule}</b>", styles['Heading2']))

        if not isinstance(details, dict):
            details = {
                "error": f"Unexpected report shape ({type(details).__name__}): {details!r}",
            }

        if details.get("error"):
            elements.append(Paragraph(f"❌ Error: {details['error']}", styles['Normal']))
        else:
            elements.append(Paragraph(f"Title: {details.get('title','')}", styles['Normal']))
            elements.append(Paragraph(f"Status: {details.get('status','')}", styles['Normal']))
            elements.append(Paragraph(f"Group: {details.get('input_kind','')}", styles['Normal']))
            if details.get("verification"):
                elements.append(Paragraph("Verification:", styles['Italic']))
                for line in str(details["verification"]).splitlines():
                    if line.strip():
                        elements.append(Paragraph(escape(line), styles['Normal']))
                    else:
                        elements.append(Spacer(1, 6))
            if details.get("remediation"):
                elements.append(Paragraph("Remediation:", styles['Italic']))
                for line in str(details["remediation"]).splitlines():
                    if line.strip():
                        elements.append(Paragraph(escape(line), styles['Normal']))
                    else:
                        elements.append(Spacer(1, 6))

            violations = details.get("violations")
            if violations:
                elements.append(Paragraph("Violations:", styles['Italic']))
                if isinstance(violations, (list, tuple)):
                    for v in violations:
                        elements.append(Paragraph(f"- {v}", styles['Normal']))
                else:
                    elements.append(Paragraph(f"- {violations}", styles['Normal']))

        elements.append(Spacer(1, 12))

    doc.build(elements)

if __name__ == "__main__":
    main()