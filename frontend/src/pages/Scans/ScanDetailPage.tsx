import React, { useState, useEffect, useCallback, JSX } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
	ArrowLeft,
	CheckCircle,
	XCircle,
	Clock,
	Loader2,
	AlertCircle,
	FileText,
	Shield,
	AlertTriangle,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { getScan } from "../../api/client";
import { RelativeTime, relativeTimePresetClass } from "../../components/RelativeTime";

type ScanDetailPageProps = {
	sidebarWidth?: number;
	isDarkMode?: boolean;
};

type ScanResult = {
	control_id?: string | number;
	status?: string;
	title?: string;
	description?: string;
	message?: string;
};

type ScanDetail = {
	id?: number | string;
	status?: string;
	benchmark?: string;
	version?: string;
	connection_name?: string;
	m365_connection_id?: number | string;
	started_at?: string | null;
	created_at?: string | null;
	finished_at?: string | null;
	completed_at?: string | null;
	total_controls?: number;
	passed_count?: number;
	failed_count?: number;
	error_count?: number;
	skipped_count?: number;
	results?: ScanResult[];
	error?: string;
};

function getErrorMessage(err: unknown, fallback: string): string {
	if (err instanceof Error && err.message) return err.message;
	if ((err as { message?: string })?.message)
		return (err as { message: string }).message;
	return fallback;
}

function compareControlIdAscending(a: ScanResult, b: ScanResult): number {
	const aId = (a?.control_id ?? "").toString();
	const bId = (b?.control_id ?? "").toString();
	const aParts = aId.split(".").map((s) => Number.parseInt(s, 10));
	const bParts = bId.split(".").map((s) => Number.parseInt(s, 10));

	const len = Math.max(aParts.length, bParts.length);
	for (let i = 0; i < len; i++) {
		const av = Number.isFinite(aParts[i]) ? aParts[i] : -1;
		const bv = Number.isFinite(bParts[i]) ? bParts[i] : -1;
		if (av !== bv) return av - bv;
	}
	return aId.localeCompare(bId);
}

const statusIconMap: Record<string, string> = {
	completed: "text-emerald-500",
	failed: "text-red-500",
	running: "text-blue-500",
	pending: "text-orange-500",
};

const resultStatusColors: Record<
	string,
	{ border: string; icon: string; badge: string; badgeBg: string }
> = {
	passed: {
		border: "border-l-emerald-500",
		icon: "text-emerald-500",
		badge: "text-emerald-500",
		badgeBg: "bg-emerald-500/15",
	},
	failed: {
		border: "border-l-red-500",
		icon: "text-red-500",
		badge: "text-red-500",
		badgeBg: "bg-red-500/15",
	},
	error: {
		border: "border-l-orange-500",
		icon: "text-orange-500",
		badge: "text-orange-500",
		badgeBg: "bg-orange-500/15",
	},
	pending: {
		border: "border-l-orange-500",
		icon: "text-orange-500",
		badge: "text-orange-500",
		badgeBg: "bg-orange-500/15",
	},
	skipped: {
		border: "border-l-slate-400",
		icon: "text-slate-400",
		badge: "text-slate-400",
		badgeBg: "bg-slate-500/15",
	},
	unknown: {
		border: "border-l-transparent",
		icon: "text-slate-400",
		badge: "text-slate-500",
		badgeBg: "bg-slate-500/15",
	},
};

const statusBadgeStyles: Record<string, string> = {
	completed: "bg-emerald-500/15 text-emerald-500",
	failed: "bg-red-500/15 text-red-500",
	running: "bg-blue-500/15 text-blue-500",
	pending: "bg-orange-500/15 text-orange-500",
};

const ScanDetailPage: React.FC<ScanDetailPageProps> = ({
	sidebarWidth = 220,
	isDarkMode = true,
}) => {
	const { scanId } = useParams<{ scanId: string }>();
	const navigate = useNavigate();
	const { token } = useAuth();

	const [scan, setScan] = useState<ScanDetail | null>(null);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);

	const loadScan = useCallback(async (): Promise<ScanDetail | null> => {
		if (!scanId) {
			setError("Scan ID is missing");
			return null;
		}

		try {
			const scanData = await getScan(token, scanId);
			setScan(scanData as ScanDetail);
			setError(null);
			return scanData as ScanDetail;
		} catch (err: unknown) {
			setError(getErrorMessage(err, "Failed to load scan"));
			return null;
		}
	}, [token, scanId]);

	useEffect(() => {
		async function initialLoad(): Promise<void> {
			setIsLoading(true);
			await loadScan();
			setIsLoading(false);
		}
		initialLoad();
	}, [loadScan]);

	useEffect(() => {
		if (!scan || scan.status === "completed" || scan.status === "failed") {
			return;
		}

		const interval = setInterval(async () => {
			const updatedScan = await loadScan();
			if (
				updatedScan?.status === "completed" ||
				updatedScan?.status === "failed"
			) {
				clearInterval(interval);
			}
		}, 3000);

		return () => clearInterval(interval);
	}, [scan, loadScan]);

	function getStatusIcon(status?: string): JSX.Element {
		const colorClass = statusIconMap[status || ""] || "text-orange-500";
		switch (status) {
			case "completed":
				return <CheckCircle size={20} className={colorClass} />;
			case "failed":
				return <XCircle size={20} className={colorClass} />;
			case "running":
				return (
					<Loader2
						size={20}
						className={`${colorClass} animate-spin`}
					/>
				);
			default:
				return <Clock size={20} className={colorClass} />;
		}
	}

	function getStatusText(status?: string): string {
		switch (status) {
			case "completed":
				return "Completed";
			case "failed":
				return "Failed";
			case "running":
				return "Running";
			default:
				return "Pending";
		}
	}

	function getResultIcon(status?: string): JSX.Element {
		const colors =
			resultStatusColors[status || ""] || resultStatusColors.unknown;
		switch (status) {
			case "passed":
				return <CheckCircle size={16} className={colors.icon} />;
			case "failed":
				return <XCircle size={16} className={colors.icon} />;
			case "error":
				return <AlertTriangle size={16} className={colors.icon} />;
			case "pending":
				return <Clock size={16} className={colors.icon} />;
			default:
				return <AlertCircle size={16} className={colors.icon} />;
		}
	}

	function getResultBadgeText(status?: string): string {
		switch (status) {
			case "passed":
				return "Pass";
			case "failed":
				return "Fail";
			case "error":
				return "Error";
			case "pending":
				return "Pending";
			case "skipped":
				return "Skipped";
			default:
				return "Unknown";
		}
	}

	const pageClasses = `min-h-screen p-6 transition-colors duration-300 ${
		isDarkMode
			? "bg-primary text-white"
			: "bg-slate-50 text-slate-800"
	}`;

	const cardBg = isDarkMode
		? "bg-secondary border-[var(--border-color)]"
		: "bg-white border-slate-200";

	const tertiaryBg = isDarkMode ? "bg-[var(--bg-tertiary)]" : "bg-slate-200";

	const textPrimary = isDarkMode
		? "text-[var(--text-primary)]"
		: "text-slate-800";

	const textSecondary = isDarkMode
		? "text-[var(--text-secondary)]"
		: "text-slate-500";

	const textTertiary = isDarkMode
		? "text-[var(--text-tertiary)]"
		: "text-slate-400";

	const borderColor = isDarkMode
		? "border-[var(--border-color)]"
		: "border-slate-200";

	const pageStyle = {
		marginLeft: `${sidebarWidth}px`,
		width: `calc(100% - ${sidebarWidth}px)`,
		transition: "margin-left 0.4s ease, width 0.4s ease",
	};

	if (isLoading) {
		return (
			<div className={pageClasses} style={pageStyle}>
				<div className="mx-auto max-w-250">
					<div
						className={`flex flex-col items-center justify-center py-20 text-center ${textSecondary}`}
					>
						<Loader2 size={32} className="animate-spin" />
						<p className="mt-4">Loading scan details...</p>
					</div>
				</div>
			</div>
		);
	}

	if (error || !scan) {
		return (
			<div className={pageClasses} style={pageStyle}>
				<div className="mx-auto max-w-250">
					<div
						className={`flex flex-col items-center justify-center py-20 text-center ${textSecondary}`}
					>
						<AlertCircle
							size={48}
							className={`mb-2 ${textTertiary}`}
						/>
						<h3
							className={`text-xl font-semibold ${textPrimary} mb-2`}
						>
							Failed to load scan
						</h3>
						<p>{error || "Scan not found"}</p>
						<button
							className={`mt-6 inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm ${borderColor} ${textSecondary} hover:${textPrimary} transition-colors`}
							onClick={() => navigate("/scans")}
						>
							<ArrowLeft size={16} />
							<span>Back to Scans</span>
						</button>
					</div>
				</div>
			</div>
		);
	}

	const summary = {
		total: scan.total_controls || 0,
		passed: scan.passed_count || 0,
		failed: scan.failed_count || 0,
		errors: scan.error_count || 0,
		pending:
			(scan.total_controls || 0) -
			(scan.passed_count || 0) -
			(scan.failed_count || 0) -
			(scan.error_count || 0) -
			(scan.skipped_count || 0),
	};

	const done =
		summary.passed +
		summary.failed +
		summary.errors +
		(scan.skipped_count || 0);

	const progressPercent =
		summary.total > 0
			? Math.min(100, Math.round((done / summary.total) * 100))
			: scan.status === "completed"
				? 100
				: 0;

	const progressFillColor =
		scan.status === "completed"
			? "bg-gradient-to-r from-emerald-500/90 to-emerald-500/55"
			: scan.status === "failed"
				? "bg-gradient-to-r from-red-500/90 to-red-500/55"
				: scan.status === "pending"
					? "bg-gradient-to-r from-orange-500/90 to-orange-500/55"
					: "bg-gradient-to-r from-blue-500/90 to-blue-500/55";

	const results = (scan.results || [])
		.filter((r) => (r?.status || "").toLowerCase() !== "skipped")
		.slice()
		.sort(compareControlIdAscending);

	const statCards = [
		{
			key: "total",
			icon: <FileText size={20} />,
			value: summary.total,
			label: "Total Controls",
			iconBg: "bg-slate-500/15",
			iconColor: textSecondary,
			valueColor: textPrimary,
		},
		{
			key: "passed",
			icon: <CheckCircle size={20} />,
			value: summary.passed,
			label: "Passed",
			iconBg: "bg-emerald-500/15",
			iconColor: "text-emerald-500",
			valueColor: "text-emerald-500",
		},
		{
			key: "failed",
			icon: <XCircle size={20} />,
			value: summary.failed,
			label: "Failed",
			iconBg: "bg-red-500/15",
			iconColor: "text-red-500",
			valueColor: "text-red-500",
		},
		{
			key: "errors",
			icon: <AlertTriangle size={20} />,
			value: summary.errors,
			label: "Errors",
			iconBg: "bg-orange-500/15",
			iconColor: "text-orange-500",
			valueColor: "text-orange-500",
		},
	];

	return (
		<div className={pageClasses} style={pageStyle}>
			<div className="mx-auto max-w-250">
				{/* Back button */}
				<div className="mb-6">
					<button
						className={`inline-flex items-center gap-2 bg-transparent border-none text-sm cursor-pointer py-2 transition-colors ${textSecondary} hover:${textPrimary}`}
						onClick={() => navigate("/scans")}
					>
						<ArrowLeft size={20} />
						<span>Back to Scans</span>
					</button>
				</div>

				{/* Header card */}
				<div className={`rounded-xl border p-6 mb-6 ${cardBg}`}>
					<div className="flex gap-4 items-center mb-5 max-md:flex-col max-md:items-start">
						<div className="flex justify-center items-center w-14 h-14 text-teal-400 rounded-xl bg-teal-400/15">
							<Shield size={32} />
						</div>
						<div className="flex-1">
							<h1
								className={`text-[22px] font-semibold m-0 mb-1 ${textPrimary}`}
							>
								{scan.benchmark || "Compliance Scan"}
							</h1>
							<p className={`text-sm m-0 ${textSecondary}`}>
								{scan.version || ""}
							</p>
						</div>
						<span
							className={`inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium ${
								statusBadgeStyles[scan.status || ""] ||
								statusBadgeStyles.pending
							}`}
						>
							{getStatusIcon(scan.status)}
							{getStatusText(scan.status)}
						</span>
					</div>

					<div
						className={`flex gap-8 pt-4 border-t max-md:flex-col max-md:gap-4 ${borderColor}`}
					>
						<div className="flex flex-col gap-1">
							<span
								className={`text-xs font-medium uppercase tracking-wide ${textTertiary}`}
							>
								Connection
							</span>
							<span className={`text-sm ${textPrimary}`}>
								{scan.connection_name ||
									(scan.m365_connection_id
										? `Connection #${scan.m365_connection_id}`
										: "-")}
							</span>
						</div>
						<div className="flex flex-col gap-1">
							<span
								className={`text-xs font-medium uppercase tracking-wide ${textTertiary}`}
							>
								Started
							</span>
							<div className={`text-sm ${textPrimary}`}>
								<RelativeTime value={scan.started_at ?? scan.created_at} preset="meta" />
							</div>
						</div>
						<div className="flex flex-col gap-1">
							<span
								className={`text-xs font-medium uppercase tracking-wide ${textTertiary}`}
							>
								Completed
							</span>
							{scan.finished_at || scan.completed_at ? (
								<div className={`text-sm ${textPrimary}`}>
									<RelativeTime value={scan.finished_at ?? scan.completed_at} preset="meta" />
								</div>
							) : (
								<div className={`text-sm ${textPrimary}`}>
									<div className={relativeTimePresetClass("meta")}>
										{scan.status === "pending" ||
										scan.status === "running"
											? "In progress"
											: "-"}
									</div>
								</div>
							)}
						</div>
					</div>
				</div>

				{/* Progress card */}
				{(scan.status === "pending" || scan.status === "running") && (
					<div
						className={`rounded-xl border p-6 text-center mb-6 ${cardBg}`}
					>
						<div className="flex flex-col gap-4 items-center">
							<Loader2
								size={24}
								className="text-teal-400 animate-spin"
							/>
							<div>
								<h3
									className={`text-lg font-semibold m-0 mb-1 ${textPrimary}`}
								>
									Scan in Progress
								</h3>
								<p className={`text-sm m-0 ${textSecondary}`}>
									{scan.status === "pending"
										? "Waiting to start..."
										: `Evaluating controls... ${done} of ${summary.total} complete`}
								</p>
							</div>
						</div>

						<div className="mt-4">
							<div className="overflow-hidden w-full h-2.5 rounded-full border border-slate-400/20 bg-slate-500/20">
								<div
									className={`h-full rounded-full transition-all duration-300 ${progressFillColor}`}
									style={{ width: `${progressPercent}%` }}
								/>
							</div>
							<div
								className={`mt-2.5 flex items-center justify-center gap-2 text-xs ${textTertiary}`}
							>
								<span>
									{done}/{summary.total} controls
								</span>
								<span>•</span>
								<span>{progressPercent}%</span>
							</div>
						</div>
					</div>
				)}

				{/* Stats grid */}
				<div className="grid grid-cols-4 gap-4 mb-6 max-md:grid-cols-2 max-[480px]:grid-cols-1">
					{statCards.map((stat) => (
						<div
							key={stat.key}
							className={`flex items-center gap-4 rounded-xl border p-5 ${cardBg}`}
						>
							<div
								className={`flex h-11 w-11 items-center justify-center rounded-[10px] ${stat.iconBg} ${stat.iconColor}`}
							>
								{stat.icon}
							</div>
							<div className="flex flex-col">
								<span
									className={`text-[28px] font-bold leading-none ${stat.valueColor}`}
								>
									{stat.value}
								</span>
								<span
									className={`mt-1 text-[13px] ${textSecondary}`}
								>
									{stat.label}
								</span>
							</div>
						</div>
					))}
				</div>

				{/* Results section */}
				{results.length > 0 && (
					<div className={`rounded-xl border p-6 ${cardBg}`}>
						<h2
							className={`text-lg font-semibold m-0 mb-5 ${textPrimary}`}
						>
							Control Results
						</h2>
						<div className="flex flex-col gap-3">
							{results.map((result, index) => {
								const status = result.status || "unknown";
								const colors =
									resultStatusColors[status] ||
									resultStatusColors.unknown;
								const isPending = status === "pending";
								const isSkipped = status === "skipped";

								return (
									<div
										key={result.control_id || index}
										className={`rounded-lg border-l-[3px] p-4 ${tertiaryBg} ${colors.border} ${
											isPending ? "opacity-70" : ""
										} ${isSkipped ? "opacity-60" : ""}`}
									>
										<div className="flex gap-3 justify-between items-start max-md:flex-col max-md:gap-2">
											<div className="flex flex-1 gap-2.5 items-center">
												{getResultIcon(result.status)}
												<span
													className={`rounded px-2 py-0.5 font-mono text-xs ${textTertiary} ${
														isDarkMode
															? "bg-secondary"
															: "bg-white"
													}`}
												>
													{result.control_id}
												</span>
												<h4
													className={`m-0 text-sm font-medium ${textPrimary}`}
												>
													{result.title ||
														result.control_id}
												</h4>
											</div>
											<span
												className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide max-md:self-start ${colors.badgeBg} ${colors.badge}`}
											>
												{getResultBadgeText(
													result.status,
												)}
											</span>
										</div>
										{result.description && (
											<p
												className={`ml-6.5 mt-3 text-[13px] leading-relaxed ${textSecondary}`}
											>
												{result.description}
											</p>
										)}
										{result.message && (
											<p
												className={`ml-6.5 mt-2 text-xs italic ${textTertiary}`}
											>
												{result.message}
											</p>
										)}
									</div>
								);
							})}
						</div>
					</div>
				)}

				{/* Error card */}
				{scan.status === "failed" && scan.error && (
					<div className="flex gap-3 items-start p-5 mt-6 rounded-xl border border-red-500/30 bg-red-500/10">
						<AlertCircle
							size={20}
							className="text-red-500 shrink-0"
						/>
						<div>
							<h4 className="m-0 mb-2 text-base font-semibold text-red-500">
								Scan Failed
							</h4>
							<p className={`m-0 text-sm ${textPrimary}`}>
								{scan.error}
							</p>
						</div>
					</div>
				)}
			</div>
		</div>
	);
};

export default ScanDetailPage;
