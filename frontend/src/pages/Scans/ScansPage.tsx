import React, { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
	Search,
	Plus,
	CheckCircle,
	XCircle,
	Clock,
	Loader2,
	AlertCircle,
	PlayCircle,
	Trash2,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
	getScans,
	getConnections,
	getBenchmarks,
	createScan,
	deleteScan,
	getSettings,
} from "../../api/client";
import { RelativeTime } from "../../components/RelativeTime";

type ScansPageProps = {
	sidebarWidth?: number;
	isDarkMode?: boolean;
};

type Scan = {
	id: number | string;
	status?: string;
	benchmark?: string;
	version?: string;
	connection_name?: string;
	m365_connection_id?: number | string;
	started_at?: string | null;
	created_at?: string | null;
	passed_count?: number;
	failed_count?: number;
	error_count?: number;
	total_controls?: number;
};

type Connection = {
	id: number | string;
	name: string;
};

type Benchmark = {
	framework: string;
	slug: string;
	version: string;
	name: string;
};

type NewScanFormData = {
	m365_connection_id: string;
	benchmark_key: string;
};

type LocationState = {
	openNewScan?: boolean;
	preselect?: {
		m365_connection_id?: number | string;
		benchmark_key?: string;
	};
};

const ScansPage: React.FC<ScansPageProps> = ({
	sidebarWidth = 220,
	isDarkMode = true,
}) => {
	const navigate = useNavigate();
	const location = useLocation();
	const { token } = useAuth();

	const [scans, setScans] = useState<Scan[]>([]);
	const [connections, setConnections] = useState<Connection[]>([]);
	const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);
	const [deletingId, setDeletingId] = useState<number | string | null>(null);
	const [confirmDeleteEnabled, setConfirmDeleteEnabled] =
		useState<boolean>(true);

	const navState = (location.state as LocationState | null) ?? null;

	const [showForm, setShowForm] = useState<boolean>(!!navState?.openNewScan);
	const [formData, setFormData] = useState<NewScanFormData>({
		m365_connection_id: navState?.preselect?.m365_connection_id
			? String(navState.preselect.m365_connection_id)
			: "",
		benchmark_key: navState?.preselect?.benchmark_key || "",
	});
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
	const appliedNavStateRef = useRef<boolean>(false);
	const stableStartedAtRef = useRef<Record<string, string>>({});

	const loadScans = useCallback(async (): Promise<void> => {
		try {
			const scansData = await getScans(token);
			setScans(scansData);
		} catch (err: unknown) {
			console.error("Failed to refresh scans:", err);
		}
	}, [token]);

	useEffect(() => {
		async function loadData(): Promise<void> {
			setIsLoading(true);
			setError(null);
			try {
				const [scansData, connectionsData, benchmarksData] =
					await Promise.all([
						getScans(token),
						getConnections(token),
						getBenchmarks(token),
					]);
				setScans(scansData);
				setConnections(connectionsData);
				setBenchmarks(benchmarksData);
			} catch (err: unknown) {
				setError((err as any)?.message || "Failed to load data");
			} finally {
				setIsLoading(false);
			}
		}

		loadData();
	}, [token]);

	useEffect(() => {
		if (appliedNavStateRef.current) return;
		const nav = (location.state as LocationState | null) ?? null;
		if (!nav?.openNewScan) return;
		appliedNavStateRef.current = true;
		setShowForm(true);
		setFormData((prev) => ({
			...prev,
			m365_connection_id: nav?.preselect?.m365_connection_id
				? String(nav.preselect.m365_connection_id)
				: prev.m365_connection_id,
			benchmark_key: nav?.preselect?.benchmark_key || prev.benchmark_key,
		}));
	}, [location]);

	useEffect(() => {
		async function loadSettings(): Promise<void> {
			try {
				const settings = await getSettings(token);
				setConfirmDeleteEnabled(
					settings?.confirm_delete_enabled ?? true,
				);
			} catch {
				setConfirmDeleteEnabled(true);
			}
		}

		loadSettings();
	}, [token]);

	useEffect(() => {
		const hasPendingScans = scans.some(
			(scan) => scan.status === "pending" || scan.status === "running",
		);
		if (!hasPendingScans) return;
		const interval = setInterval(loadScans, 5000);
		return () => clearInterval(interval);
	}, [scans, loadScans]);

	function handleChange(
		e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>,
	): void {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
	}

	async function handleSubmit(
		e: React.FormEvent<HTMLFormElement>,
	): Promise<void> {
		e.preventDefault();
		setIsSubmitting(true);
		setError(null);

		try {
			const [framework, benchmark, version] =
				formData.benchmark_key.split("|");
			const newScan = await createScan(token, {
				m365_connection_id: parseInt(formData.m365_connection_id, 10),
				framework,
				benchmark,
				version,
			});
			setScans((prev) => [newScan, ...prev]);
			setFormData({ m365_connection_id: "", benchmark_key: "" });
			setShowForm(false);
		} catch (err: unknown) {
			setError((err as any)?.message || "Failed to create scan");
		} finally {
			setIsSubmitting(false);
		}
	}

	function getStatusIcon(status?: string): React.ReactNode {
		switch (status) {
			case "completed":
				return <CheckCircle size={16} className="text-emerald-500" />;
			case "failed":
				return <XCircle size={16} className="text-red-500" />;
			case "running":
				return (
					<Loader2 size={16} className="text-blue-500 animate-spin" />
				);
			default:
				return <Clock size={16} className="text-orange-500" />;
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

	function getStableStartedAt(scan: Scan): string | null {
		const candidate = scan.started_at || scan.created_at || null;
		if (!candidate) return null;

		const key = String(scan.id);
		const existing = stableStartedAtRef.current[key];
		if (!existing) {
			stableStartedAtRef.current[key] = candidate;
			return candidate;
		}

		const parseTimestampMs = (value: string): number => {
			const direct = new Date(value).getTime();
			if (!Number.isNaN(direct)) return direct;
			const normalized = value.trim().replace(" ", "T").replace(/(\.\d{3})\d+/, "$1");
			return new Date(normalized).getTime();
		};

		const candidateMs = parseTimestampMs(candidate);
		const existingMs = parseTimestampMs(existing);
		if (Number.isNaN(existingMs)) {
			stableStartedAtRef.current[key] = candidate;
			return candidate;
		}
		if (!Number.isNaN(candidateMs) && candidateMs < existingMs) {
			stableStartedAtRef.current[key] = candidate;
			return candidate;
		}
		return existing;
	}

	function getStatusBadgeClasses(status?: string): string {
		const base =
			"inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium";
		switch (status) {
			case "completed":
				return `${base} bg-emerald-500/15 text-emerald-500`;
			case "failed":
				return `${base} bg-red-500/15 text-red-500`;
			case "running":
				return `${base} bg-blue-500/15 text-blue-500`;
			default:
				return `${base} bg-orange-500/15 text-orange-500`;
		}
	}

	async function handleDelete(scanId: number | string): Promise<void> {
		if (confirmDeleteEnabled) {
			const ok = window.confirm(
				"Are you sure you want to delete this scan? This action cannot be undone.",
			);
			if (!ok) return;
		}

		setDeletingId(scanId);
		setError(null);
		try {
			await deleteScan(token, scanId);
			setScans((prev) => prev.filter((s) => s.id !== scanId));
		} catch (err: unknown) {
			setError((err as any)?.message || "Failed to delete scan");
		} finally {
			setDeletingId(null);
		}
	}

	if (isLoading) {
		return (
			<div
				className={`min-h-screen p-6 transition-colors duration-300 ${
					isDarkMode ? "bg-primary" : "bg-slate-50"
				}`}
				style={{
					marginLeft: `${sidebarWidth}px`,
					width: `calc(100% - ${sidebarWidth}px)`,
					transition: "margin-left 0.4s ease, width 0.4s ease",
				}}
			>
				<div className="mx-auto max-w-300">
					<div className="flex flex-col justify-center items-center py-16 text-(--text-secondary)">
						<Loader2 size={32} className="animate-spin" />
						<p className="mt-4">Loading scans...</p>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div
			className={`min-h-screen p-6 transition-colors duration-300 ${
				isDarkMode ? "bg-primary" : "bg-slate-50"
			}`}
			style={{
				marginLeft: `${sidebarWidth}px`,
				width: `calc(100% - ${sidebarWidth}px)`,
				transition: "margin-left 0.4s ease, width 0.4s ease",
			}}
		>
			<div className="mx-auto max-w-300">
				{/* Page Header */}
				<div className="flex justify-between items-center mb-6 max-md:flex-col max-md:items-start max-md:gap-4">
					<div className="flex gap-4 items-center text-(--text-primary)">
						<Search size={24} className="text-blue-500" />
						<div>
							<h1 className="m-0 text-2xl font-bold text-(--text-primary)">
								Compliance Scans
							</h1>
							<p className="m-0 text-sm text-(--text-secondary)">
								Run and manage compliance scans against your
								M365 connections
							</p>
						</div>
					</div>
					<button
						className="inline-flex gap-2 items-center py-2 px-4 text-sm font-medium text-white bg-blue-500 rounded-lg transition hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
						onClick={() => setShowForm(!showForm)}
						disabled={connections.length === 0}
					>
						<Plus size={16} />
						<span>New Scan</span>
					</button>
				</div>

				{/* Error Banner */}
				{error && (
					<div className="flex gap-2 items-center py-3 px-4 mb-6 text-red-500 rounded-lg border bg-red-500/10 border-red-500/30">
						<AlertCircle size={18} />
						<span>{error}</span>
					</div>
				)}

				{/* Warning Banner */}
				{connections.length === 0 && !isLoading && (
					<div className="flex gap-2 items-center py-3 px-4 mb-6 text-orange-500 rounded-lg border bg-orange-500/10 border-orange-500/30">
						<AlertCircle size={18} />
						<span>
							You need to add a connection before you can run
							scans.
						</span>
					</div>
				)}

				{/* New Scan Form */}
				{showForm && (
					<div className="p-6 mb-6 rounded-xl border bg-secondary border-(--border-color)">
						<h3 className="mb-5 text-lg font-semibold text-(--text-primary)">
							New Compliance Scan
						</h3>
						<form onSubmit={handleSubmit}>
							<div className="grid grid-cols-2 gap-4 max-md:grid-cols-1">
								<div className="mb-4">
									<label
										htmlFor="m365_connection_id"
										className="block mb-2 text-sm font-medium text-(--text-secondary)"
									>
										Cloud Platform
									</label>
									<select
										id="m365_connection_id"
										name="m365_connection_id"
										value={formData.m365_connection_id}
										onChange={handleChange}
										required
										disabled={isSubmitting}
										className="py-2.5 px-3.5 w-full text-sm rounded-lg border transition-colors duration-200 cursor-pointer focus:border-blue-500 focus:outline-none disabled:opacity-60 disabled:cursor-not-allowed bg-(--bg-tertiary) border-(--border-color) text-(--text-primary)"
									>
										<option value="" className="bg-primary">
											Select a cloud platform
										</option>
										{connections.map((conn) => (
											<option
												key={conn.id}
												value={conn.id}
												className="bg-primary"
											>
												{conn.name}
											</option>
										))}
									</select>
								</div>

								<div className="mb-4">
									<label
										htmlFor="benchmark_key"
										className="block mb-2 text-sm font-medium text-(--text-secondary)"
									>
										Benchmark
									</label>
									<select
										id="benchmark_key"
										name="benchmark_key"
										value={formData.benchmark_key}
										onChange={handleChange}
										required
										disabled={isSubmitting}
										className="py-2.5 px-3.5 w-full text-sm rounded-lg border transition-colors duration-200 cursor-pointer focus:border-blue-500 focus:outline-none disabled:opacity-60 disabled:cursor-not-allowed bg-(--bg-tertiary) border-(--border-color) text-(--text-primary)"
									>
										<option value="" className="bg-primary">
											Select a benchmark
										</option>
										{benchmarks.map((bench) => (
											<option
												key={`${bench.framework}|${bench.slug}|${bench.version}`}
												value={`${bench.framework}|${bench.slug}|${bench.version}`}
												className="bg-primary"
											>
												{bench.name} ({bench.version})
											</option>
										))}
									</select>
								</div>
							</div>

							<div className="flex gap-3 justify-end mt-2">
								<button
									type="button"
									className="flex gap-2 items-center py-2 px-4 font-medium rounded-lg border-none cursor-pointer outline-none text-[14px] [transition:all_0.3s_ease] bg-secondary"
									onClick={() => setShowForm(false)}
									disabled={isSubmitting}
								>
									Cancel
								</button>
								<button
									type="submit"
									className="flex gap-2 items-center py-2 px-4 font-medium rounded-lg border-none cursor-pointer outline-none text-[14px] [transition:all_0.3s_ease] bg-primary"
									disabled={isSubmitting}
								>
									{isSubmitting ? (
										<>
											<Loader2
												size={16}
												className="animate-spin"
											/>
											<span>Starting...</span>
										</>
									) : (
										<>
											<PlayCircle size={16} />
											<span>Start Scan</span>
										</>
									)}
								</button>
							</div>
						</form>
					</div>
				)}

				{/* Scans List */}
				<div className="overflow-hidden rounded-xl border border-dashed bg-secondary border-slate-600">
					{scans.length === 0 ? (
						<div className="py-16 px-5 text-center">
							<Search
								size={48}
								className="mx-auto mb-4 text-(--text-tertiary)"
							/>
							<h3 className="mb-2 text-lg font-semibold text-(--text-primary)">
								No scans yet
							</h3>
							<p className="text-sm text-(--text-secondary)">
								Run your first compliance scan to see results
								here.
							</p>
						</div>
					) : (
						<table className="w-full border-collapse max-md:block max-md:overflow-x-auto">
							<thead>
								<tr>
									<th className="py-4 px-5 text-xs font-semibold tracking-wider text-left uppercase border-b text-(--text-secondary) border-(--border-color)] bg-(--bg-tertiary)">
										Status
									</th>
									<th className="py-4 px-5 text-xs font-semibold tracking-wider text-left uppercase border-b text-(--text-secondary) border-(--border-color)] bg-(--bg-tertiary)">
										Benchmark
									</th>
									<th className="py-4 px-5 text-xs font-semibold tracking-wider text-left uppercase border-b text-(--text-secondary) border-(--border-color)] bg-(--bg-tertiary)">
										Connection
									</th>
									<th className="py-4 px-5 text-xs font-semibold tracking-wider text-left uppercase border-b text-(--text-secondary) border-(--border-color)] bg-(--bg-tertiary)">
										Started
									</th>
									<th className="py-4 px-5 text-xs font-semibold tracking-wider text-left uppercase border-b text-(--text-secondary) border-(--border-color)] bg-(--bg-tertiary)">
										Results
									</th>
									<th className="text-right px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary) w-[1%] whitespace-nowrap">
										Actions
									</th>
								</tr>
							</thead>
							<tbody>
								{scans.map((scan) => (
									<tr
										key={scan.id}
										onClick={() =>
											navigate(`/scans/${scan.id}`)
										}
										className="cursor-pointer transition-colors duration-200 hover:bg-(--bg-tertiary) last:[&>td]:border-b-0"
									>
										<td className="py-4 px-5 text-sm border-b text-(--text-primary) border-(--border-color)]">
											<span
												className={getStatusBadgeClasses(
													scan.status,
												)}
											>
												{getStatusIcon(scan.status)}
												{getStatusText(scan.status)}
											</span>
										</td>
										<td className="py-4 px-5 text-sm border-b text-(--text-primary) border-(--border-color)]">
											<span className="block font-medium">
												{scan.benchmark || "-"}
											</span>
											<span className="block text-xs text-(--text-tertiary)">
												{scan.version || ""}
											</span>
										</td>
										<td className="py-4 px-5 text-sm border-b text-(--text-primary) border-(--border-color)]">
											{scan.connection_name ||
												(scan.m365_connection_id
													? `Connection #${scan.m365_connection_id}`
													: "-")}
										</td>
										<td className="py-4 px-5 text-sm border-b text-(--text-primary) border-(--border-color)]">
											{(() => {
												const dateString = getStableStartedAt(scan);
												if (!dateString) return "-";
												return (
													<RelativeTime value={dateString} preset="scansTableCell" />
												);
											})()}
										</td>
										<td className="py-4 px-5 text-sm border-b text-(--text-primary) border-(--border-color)]">
											{scan.status === "completed" ||
											scan.status === "running" ? (
												<div className="flex gap-3 text-[13px]">
													<span className="text-emerald-500">
														{scan.passed_count || 0}{" "}
														passed
													</span>
													<span className="text-red-500">
														{scan.failed_count || 0}{" "}
														failed
													</span>
													{scan.status ===
														"running" &&
														(scan.total_controls ||
															0) > 0 && (
															<span>
																(
																{(scan.passed_count ||
																	0) +
																	(scan.failed_count ||
																		0) +
																	(scan.error_count ||
																		0)}
																/
																{scan.total_controls ||
																	0}
																)
															</span>
														)}
												</div>
											) : (
												"-"
											)}
										</td>
										<td
											className="text-right px-5 py-4 text-sm border-b border-(--border-color)] w-[1%] whitespace-nowrap"
											onClick={(
												e: React.MouseEvent<HTMLTableCellElement>,
											) => e.stopPropagation()}
										>
											<button
												className="flex gap-2 items-center py-1.5 px-2.5 font-medium rounded-lg border-none cursor-pointer outline-none [transition:all_0.3s_ease] text-[rgb(var(--accent-bad))] text-[13px]"
												onClick={() =>
													handleDelete(scan.id)
												}
												disabled={
													deletingId === scan.id
												}
											>
												{deletingId === scan.id ? (
													<Loader2
														size={14}
														className="animate-spin"
													/>
												) : (
													<Trash2 size={14} />
												)}
												<span>
													{deletingId === scan.id
														? "Deleting..."
														: "Delete"}
												</span>
											</button>
										</td>
									</tr>
								))}
							</tbody>
						</table>
					)}
				</div>
			</div>
		</div>
	);
};

export default ScansPage;
