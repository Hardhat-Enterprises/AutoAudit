import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

const MARGIN_PT = 24;

/**
 * Per-capture limit for canvas device pixels on an edge. Stays under strict
 * browser caps (Safari ~4096) so html2canvas output is valid before PDF paging.
 */
const MAX_CAPTURE_DEVICE_EDGE = 4096;

/** Default raster scale; reduced automatically if the element is very wide. */
const DEFAULT_CAPTURE_SCALE = 2;

type PdfLayoutState = {
	/** Used content height on the current PDF page (pt), from top margin downward. */
	yUsedPt: number;
};

function effectiveCaptureScale(scrollWidthCss: number, requested: number): number {
	const w = Math.max(1, Math.ceil(scrollWidthCss));
	const maxScale = MAX_CAPTURE_DEVICE_EDGE / w;
	return Math.max(1, Math.min(requested, maxScale));
}

/** Max element height (CSS px) per html2canvas call at the given scale. */
function maxChunkCssHeight(scale: number): number {
	return Math.max(160, Math.floor(MAX_CAPTURE_DEVICE_EDGE / scale));
}

const sharedHtml2CanvasOptions = {
	useCORS: true,
	logging: false,
	backgroundColor: "#ffffff" as const,
};

/**
 * Rasterizes one canvas (one vertical segment of the report) into the PDF,
 * continuing mid-page when a previous segment left space below the margin.
 */
function appendCanvasToPdfContinuous(
	pdf: jsPDF,
	canvas: HTMLCanvasElement,
	contentWidth: number,
	contentHeight: number,
	layout: PdfLayoutState,
): void {
	const imgScaledHeightPt =
		(canvas.height * contentWidth) / canvas.width;
	if (imgScaledHeightPt <= 0) {
		return;
	}

	let yPt = 0;
	while (yPt < imgScaledHeightPt - 1e-4) {
		const spaceLeftPt = contentHeight - layout.yUsedPt;
		const sliceHeightPt = Math.min(
			spaceLeftPt,
			imgScaledHeightPt - yPt,
		);
		if (sliceHeightPt <= 1e-6) {
			pdf.addPage();
			layout.yUsedPt = 0;
			continue;
		}

		const sourceY = (yPt / imgScaledHeightPt) * canvas.height;
		const sourceH = (sliceHeightPt / imgScaledHeightPt) * canvas.height;

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
			MARGIN_PT + layout.yUsedPt,
			contentWidth,
			sliceHeightPt,
		);

		yPt += sliceHeightPt;
		layout.yUsedPt += sliceHeightPt;

		if (layout.yUsedPt >= contentHeight - 1e-3) {
			layout.yUsedPt = 0;
			if (yPt < imgScaledHeightPt - 1e-4) {
				pdf.addPage();
			}
		}
	}
}

/** Sentinel: do not copy this computed property onto the clone. */
const SKIP_PROPERTY = "__PDF_EXPORT_SKIP_PROPERTY__";

/** Longhand color properties we inline when we cannot mirror the full tree. */
const COLOR_PROPERTIES = [
	"color",
	"background-color",
	"border-top-color",
	"border-right-color",
	"border-bottom-color",
	"border-left-color",
	"outline-color",
	"text-decoration-color",
	"caret-color",
	"column-rule-color",
] as const;

const SKIP_COMPUTED_PROPS = new Set([
	"transition",
	"transition-delay",
	"transition-duration",
	"transition-property",
	"transition-timing-function",
	"animation",
	"animation-delay",
	"animation-direction",
	"animation-duration",
	"animation-fill-mode",
	"animation-iteration-count",
	"animation-name",
	"animation-play-state",
	"animation-timing-function",
]);

/** How to pick a safe fallback when oklch cannot be resolved for html2canvas. */
type ColorRole = "background" | "text" | "border" | "accent";

function fallbackColor(role: ColorRole): string {
	switch (role) {
		case "background":
			return "#f8fafc";
		case "text":
			return "#0f172a";
		case "border":
			return "#e2e8f0";
		case "accent":
			return "#0d9488";
		default:
			return "#64748b";
	}
}

function colorRoleForCssProperty(propName: string): ColorRole {
	const p = propName.toLowerCase();
	if (p === "background-color" || p === "flood-color") {
		return "background";
	}
	if (p === "fill") {
		return "accent";
	}
	if (p === "stroke") {
		return "border";
	}
	if (p === "color" || p === "caret-color") {
		return "text";
	}
	if (p === "text-decoration-color") {
		return "text";
	}
	if (p.startsWith("border-") && p.endsWith("-color")) {
		return "border";
	}
	if (p === "outline-color" || p === "column-rule-color") {
		return "border";
	}
	if (p === "stop-color" || p === "lighting-color") {
		return "accent";
	}
	return "text";
}

function usesUnsupportedColorFunction(value: string): boolean {
	const v = value.toLowerCase();
	return (
		v.includes("oklch(") ||
		v.includes("lab(") ||
		v.includes("lch(") ||
		v.includes("oklab(")
	);
}

/** Pull the first color-like token from a CSS gradient string for a solid fallback. */
function firstCssColorToken(value: string): string | null {
	const match = value.match(
		/(oklch\([^)]+\)|oklab\([^)]+\)|lab\([^)]+\)|lch\([^)]+\)|#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))/i,
	);
	return match ? match[1] : null;
}

/**
 * Resolves a browser-supported color string (including oklch) to something
 * html2canvas can parse, using the canvas fillStyle round-trip.
 * Never falls back to black for surfaces — that produced unreadable PDFs.
 */
function normalizeColorForCapture(
	win: Window,
	cssColor: string,
	role: ColorRole,
): string {
	const t = cssColor.trim();
	if (!t || t === "transparent" || t === "inherit") {
		return t;
	}
	if (!usesUnsupportedColorFunction(t)) {
		return t;
	}
	const canvas = win.document.createElement("canvas");
	canvas.width = 1;
	canvas.height = 1;
	const ctx = canvas.getContext("2d");
	if (!ctx) {
		return fallbackColor(role);
	}
	try {
		ctx.fillStyle = "#000000";
		ctx.fillStyle = t;
		const resolved = ctx.fillStyle;
		if (
			typeof resolved === "string" &&
			!usesUnsupportedColorFunction(resolved)
		) {
			return resolved;
		}
	} catch {
		/* invalid color */
	}
	return fallbackColor(role);
}

function normalizePropertyValueForHtml2Canvas(
	win: Window,
	propName: string,
	value: string,
): string {
	if (!usesUnsupportedColorFunction(value)) {
		return value;
	}
	const lower = propName.toLowerCase();
	if (lower === "background-image" || lower.endsWith("-image")) {
		return "none";
	}
	if (
		lower.includes("shadow") ||
		lower === "filter" ||
		lower === "backdrop-filter"
	) {
		return "none";
	}
	if (
		lower.includes("color") ||
		lower === "fill" ||
		lower === "stroke" ||
		lower === "stop-color" ||
		lower === "flood-color" ||
		lower === "lighting-color"
	) {
		const role = colorRoleForCssProperty(lower);
		return normalizeColorForCapture(win, value, role);
	}
	// Unknown property still containing oklch — do not write `initial` (breaks capture).
	return SKIP_PROPERTY;
}

/**
 * Copies **used** computed styles from the live DOM onto the clone, then removes
 * author stylesheets from the clone. This prevents html2canvas from parsing
 * Tailwind v4 rules that still contain `oklch()`.
 */
function mirrorComputedStylesOntoClone(
	originalRoot: HTMLElement,
	clonedRoot: HTMLElement,
): boolean {
	const origWin = originalRoot.ownerDocument.defaultView;
	if (!origWin) {
		return false;
	}

	const originals: Element[] = [originalRoot, ...originalRoot.querySelectorAll("*")];
	const clones: Element[] = [clonedRoot, ...clonedRoot.querySelectorAll("*")];

	if (originals.length !== clones.length) {
		return false;
	}

	for (let i = 0; i < originals.length; i++) {
		const orig = originals[i];
		const clone = clones[i];
		const cloneStyle = inlineStyleOf(clone);
		if (!cloneStyle) {
			continue;
		}

		const cs = origWin.getComputedStyle(orig);

		for (let j = 0; j < cs.length; j++) {
			const name = cs.item(j);
			if (!name || SKIP_COMPUTED_PROPS.has(name)) {
				continue;
			}
			let val = cs.getPropertyValue(name);
			if (!val) {
				continue;
			}
			if (usesUnsupportedColorFunction(val)) {
				val = normalizePropertyValueForHtml2Canvas(origWin, name, val);
				if (val === SKIP_PROPERTY) {
					continue;
				}
			}
			const priority = cs.getPropertyPriority(name);
			try {
				cloneStyle.setProperty(name, val, priority);
			} catch {
				/* skip invalid combinations */
			}
		}

		if (clone instanceof SVGElement && orig instanceof SVGElement) {
			for (const attr of ["fill", "stroke"] as const) {
				const raw = clone.getAttribute(attr);
				if (raw && usesUnsupportedColorFunction(raw)) {
					const role = attr === "fill" ? "accent" : "border";
					clone.setAttribute(
						attr,
						normalizeColorForCapture(origWin, raw, role),
					);
				}
			}
		}
	}

	return true;
}

function stripAuthorStylesFromCloneDocument(doc: Document): void {
	doc.querySelectorAll('link[rel="stylesheet"]').forEach((n) => n.remove());
	doc.querySelectorAll("style").forEach((n) => n.remove());
}

function inlineStyleOf(el: Element): CSSStyleDeclaration | null {
	return "style" in el && el.style
		? (el as HTMLElement | SVGElement).style
		: null;
}

function roleForFlattenProp(prop: string): ColorRole {
	if (prop === "background-color") {
		return "background";
	}
	if (prop === "color") {
		return "text";
	}
	return "border";
}

/**
 * Fallback when clone/original node counts differ: inline common color longhands only.
 */
function flattenComputedColorsInClone(
	doc: Document,
	clonedRoot: HTMLElement,
): void {
	const win = doc.defaultView;
	if (!win) {
		return;
	}

	const nodes: Element[] = [clonedRoot, ...clonedRoot.querySelectorAll("*")];

	for (const node of nodes) {
		const cs = win.getComputedStyle(node);

		if (node instanceof SVGElement) {
			const fill = cs.getPropertyValue("fill").trim();
			if (fill && usesUnsupportedColorFunction(fill)) {
				node.setAttribute(
					"fill",
					normalizeColorForCapture(win, fill, "accent"),
				);
			}
			const stroke = cs.getPropertyValue("stroke").trim();
			if (stroke && usesUnsupportedColorFunction(stroke)) {
				node.setAttribute(
					"stroke",
					normalizeColorForCapture(win, stroke, "border"),
				);
			}
			continue;
		}

		if (!(node instanceof HTMLElement)) {
			continue;
		}

		let csHtml = cs;

		const bgImage = csHtml.getPropertyValue("background-image");
		if (
			bgImage &&
			bgImage !== "none" &&
			usesUnsupportedColorFunction(bgImage)
		) {
			node.style.setProperty("background-image", "none", "important");
			const bgColor = csHtml.getPropertyValue("background-color").trim();
			const isTransparent =
				bgColor === "transparent" ||
				bgColor === "rgba(0, 0, 0, 0)" ||
				bgColor === "";
			if (isTransparent || usesUnsupportedColorFunction(bgColor)) {
				const token = firstCssColorToken(bgImage);
				const solid =
					token == null
						? "#cbd5e1"
						: normalizeColorForCapture(win, token, "accent");
				node.style.setProperty("background-color", solid, "important");
			}
		}

		csHtml = win.getComputedStyle(node);

		for (const prop of COLOR_PROPERTIES) {
			const raw = csHtml.getPropertyValue(prop).trim();
			if (!raw) {
				continue;
			}
			const normalized = normalizeColorForCapture(
				win,
				raw,
				roleForFlattenProp(prop),
			);
			if (normalized) {
				node.style.setProperty(prop, normalized, "important");
			}
		}

		csHtml = win.getComputedStyle(node);
		const boxShadow = csHtml.getPropertyValue("box-shadow");
		if (
			boxShadow &&
			boxShadow !== "none" &&
			usesUnsupportedColorFunction(boxShadow)
		) {
			node.style.setProperty("box-shadow", "none", "important");
		}
		const textShadow = csHtml.getPropertyValue("text-shadow");
		if (
			textShadow &&
			textShadow !== "none" &&
			usesUnsupportedColorFunction(textShadow)
		) {
			node.style.setProperty("text-shadow", "none", "important");
		}
	}
}

function prepareCloneForHtml2Canvas(
	originalElement: HTMLElement,
	clonedDoc: Document,
	clonedRoot: HTMLElement,
): void {
	const mirrored = mirrorComputedStylesOntoClone(originalElement, clonedRoot);
	if (!mirrored) {
		flattenComputedColorsInClone(clonedDoc, clonedRoot);
	}
	stripAuthorStylesFromCloneDocument(clonedDoc);
}

/**
 * Renders a DOM node to a multi-page A4 PDF and triggers download in the browser.
 * Captures the node in vertical html2canvas chunks so device-pixel canvas size
 * stays within browser limits on long reports.
 */
export async function exportElementToPdf(
	element: HTMLElement,
	filename: string,
): Promise<void> {
	const pdf = new jsPDF({
		unit: "pt",
		format: "a4",
		orientation: "portrait",
	});
	const pageWidth = pdf.internal.pageSize.getWidth();
	const pageHeight = pdf.internal.pageSize.getHeight();
	const contentWidth = pageWidth - MARGIN_PT * 2;
	const contentHeight = pageHeight - MARGIN_PT * 2;

	const totalWidth = Math.max(1, Math.ceil(element.scrollWidth));
	const totalHeight = Math.max(1, Math.ceil(element.scrollHeight));
	const scale = effectiveCaptureScale(
		totalWidth,
		DEFAULT_CAPTURE_SCALE,
	);
	const chunkCss = maxChunkCssHeight(scale);

	const layout: PdfLayoutState = { yUsedPt: 0 };

	for (let y = 0; y < totalHeight; y += chunkCss) {
		const sliceH = Math.min(chunkCss, totalHeight - y);
		const canvas = await html2canvas(element, {
			...sharedHtml2CanvasOptions,
			scale,
			x: 0,
			y,
			width: totalWidth,
			height: sliceH,
			windowWidth: totalWidth,
			windowHeight: totalHeight,
			onclone: (clonedDoc, clonedRoot) => {
				prepareCloneForHtml2Canvas(element, clonedDoc, clonedRoot);
			},
		});

		appendCanvasToPdfContinuous(
			pdf,
			canvas,
			contentWidth,
			contentHeight,
			layout,
		);
	}

	pdf.save(filename);
}
