import { describe, it, expect } from "vitest";
import { buildScanExportFilename } from "./buildScanExportFilename";

describe("buildScanExportFilename", () => {
	it("uses scan id in the name", () => {
		expect(buildScanExportFilename(42)).toBe("scan-42-report.pdf");
	});

	it("stringifies string ids", () => {
		expect(buildScanExportFilename("99")).toBe("scan-99-report.pdf");
	});

	it("falls back when id is empty or undefined", () => {
		expect(buildScanExportFilename("")).toBe("scan-report.pdf");
		expect(buildScanExportFilename(undefined)).toBe("scan-report.pdf");
	});
});
