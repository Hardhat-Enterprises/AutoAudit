/**
 * File name for a client-side scan report PDF.
 */
export function buildScanExportFilename(
	scanId: string | number | undefined,
): string {
	if (scanId == null || String(scanId).trim() === "") {
		return "scan-report.pdf";
	}
	return `scan-${String(scanId)}-report.pdf`;
}
