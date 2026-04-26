import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

const MARGIN_PT = 24;

/**
 * Renders a DOM node to a multi-page A4 PDF and triggers download in the browser.
 */
export async function exportElementToPdf(
	element: HTMLElement,
	filename: string,
): Promise<void> {
	const canvas = await html2canvas(element, {
		scale: 2,
		useCORS: true,
		logging: false,
		backgroundColor: "#ffffff",
		windowWidth: element.scrollWidth,
		windowHeight: element.scrollHeight,
	});

	const pdf = new jsPDF({
		unit: "pt",
		format: "a4",
		orientation: "portrait",
	});
	const pageWidth = pdf.internal.pageSize.getWidth();
	const pageHeight = pdf.internal.pageSize.getHeight();
	const contentWidth = pageWidth - MARGIN_PT * 2;
	const contentHeight = pageHeight - MARGIN_PT * 2;

	const imgScaledHeight = (canvas.height * contentWidth) / canvas.width;
	if (imgScaledHeight <= 0) {
		pdf.save(filename);
		return;
	}

	let yOffset = 0;
	while (yOffset < imgScaledHeight) {
		if (yOffset > 0) {
			pdf.addPage();
		}
		const sliceHeightPt = Math.min(contentHeight, imgScaledHeight - yOffset);
		const sourceY = (yOffset / imgScaledHeight) * canvas.height;
		const sourceH = (sliceHeightPt / imgScaledHeight) * canvas.height;

		const slice = document.createElement("canvas");
		slice.width = canvas.width;
		slice.height = Math.max(1, Math.ceil(sourceH));
		const ctx = slice.getContext("2d");
		if (!ctx) {
			throw new Error("Could not get canvas context");
		}
		ctx.drawImage(
			canvas,
			0,
			sourceY,
			canvas.width,
			sourceH,
			0,
			0,
			canvas.width,
			sourceH,
		);

		const dataUrl = slice.toDataURL("image/png");
		pdf.addImage(
			dataUrl,
			"PNG",
			MARGIN_PT,
			MARGIN_PT,
			contentWidth,
			sliceHeightPt,
		);
		yOffset += sliceHeightPt;
	}

	pdf.save(filename);
}
