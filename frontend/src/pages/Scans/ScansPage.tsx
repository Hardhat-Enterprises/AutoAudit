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
import { formatDateTimePartsAEST } from "../../utils/helpers";

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

	function formatDate(
		dateString?: string | null,
	): ReturnType<typeof formatDateTimePartsAEST> {
		return formatDateTimePartsAEST(dateString);
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
				<div className="max-w-300 mx-auto">
					<div className="flex flex-col items-center justify-center py-16 text-(--text-secondary)">
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
			<div className="max-w-300 mx-auto">
				{/* Page Header */}
				<div className="flex items-center justify-between mb-6 max-md:flex-col max-md:items-start max-md:gap-4">
					<div className="flex items-center gap-4 text-(--text-primary)">
						<Search size={24} className="text-blue-500" />
						<div>
							<h1 className="text-2xl font-bold text-(--text-primary) m-0">
								Compliance Scans
							</h1>
							<p className="text-sm text-(--text-secondary) m-0">
								Run and manage compliance scans against your
								M365 connections
							</p>
						</div>
					</div>
					<button
						className="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
						onClick={() => setShowForm(!showForm)}
						disabled={connections.length === 0}
					>
						<Plus size={16} />
						<span>New Scan</span>
					</button>
				</div>

				{/* Error Banner */}
				{error && (
					<div className="flex items-center gap-2 px-4 py-3 rounded-lg mb-6 bg-red-500/10 border border-red-500/30 text-red-500">
						<AlertCircle size={18} />
						<span>{error}</span>
					</div>
				)}

				{/* Warning Banner */}
				{connections.length === 0 && !isLoading && (
					<div className="flex items-center gap-2 px-4 py-3 rounded-lg mb-6 bg-orange-500/10 border border-orange-500/30 text-orange-500">
						<AlertCircle size={18} />
						<span>
							You need to add a connection before you can run
							scans.
						</span>
					</div>
				)}

				{/* New Scan Form */}
				{showForm && (
					<div className="bg-secondary border border-(--border-color) rounded-xl p-6 mb-6">
						<h3 className="text-(--text-primary) text-lg font-semibold mb-5">
							New Compliance Scan
						</h3>
						<form onSubmit={handleSubmit}>
							<div className="grid grid-cols-2 gap-4 max-md:grid-cols-1">
								<div className="mb-4">
									<label
										htmlFor="m365_connection_id"
										className="block text-(--text-secondary) text-sm font-medium mb-2"
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
										className="w-full px-3.5 py-2.5 bg-(--bg-tertiary) border border-(--border-color) rounded-lg text-(--text-primary) text-sm transition-colors duration-200 cursor-pointer focus:outline-none focus:border-blue-500 disabled:opacity-60 disabled:cursor-not-allowed"
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
										className="block text-(--text-secondary) text-sm font-medium mb-2"
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
										className="w-full px-3.5 py-2.5 bg-(--bg-tertiary) border border-(--border-color) rounded-lg text-(--text-primary) text-sm transition-colors duration-200 cursor-pointer focus:outline-none focus:border-blue-500 disabled:opacity-60 disabled:cursor-not-allowed"
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

							<div className="flex justify-end gap-3 mt-2">
								<button
									type="button"
									className="flex items-center gap-2 px-4 py-2 rounded-lg text-[14px] font-medium cursor-pointer [transition:all_0.3s_ease] border-none outline-none bg-secondary"
									onClick={() => setShowForm(false)}
									disabled={isSubmitting}
								>
									Cancel
								</button>
								<button
									type="submit"
									className="flex items-center gap-2 px-4 py-2 rounded-lg text-[14px] font-medium cursor-pointer [transition:all_0.3s_ease] border-none outline-none bg-primary"
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
				<div className="bg-secondary border border-dashed border-slate-600 rounded-xl overflow-hidden">
					{scans.length === 0 ? (
						<div className="text-center py-16 px-5">
							<Search
								size={48}
								className="text-(--text-tertiary) mb-4 mx-auto"
							/>
							<h3 className="text-(--text-primary) text-lg font-semibold mb-2">
								No scans yet
							</h3>
							<p className="text-(--text-secondary) text-sm">
								Run your first compliance scan to see results
								here.
							</p>
						</div>
					) : (
						<table className="w-full border-collapse max-md:block max-md:overflow-x-auto">
							<thead>
								<tr>
									<th className="text-left px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary)">
										Status
									</th>
									<th className="text-left px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary)">
										Benchmark
									</th>
									<th className="text-left px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary)">
										Connection
									</th>
									<th className="text-left px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary)">
										Started
									</th>
									<th className="text-left px-5 py-4 text-(--text-secondary) text-xs font-semibold uppercase tracking-wider border-b border-(--border-color)] bg-(--bg-tertiary)">
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
										<td className="px-5 py-4 text-(--text-primary) text-sm border-b border-(--border-color)]">
											<span
												className={getStatusBadgeClasses(
													scan.status,
												)}
											>
												{getStatusIcon(scan.status)}
												{getStatusText(scan.status)}
											</span>
										</td>
										<td className="px-5 py-4 text-(--text-primary) text-sm border-b border-(--border-color)]">
											<span className="block font-medium">
												{scan.benchmark || "-"}
											</span>
											<span className="block text-xs text-(--text-tertiary)">
												{scan.version || ""}
											</span>
										</td>
										<td className="px-5 py-4 text-(--text-primary) text-sm border-b border-(--border-color)]">
											{scan.connection_name ||
												(scan.m365_connection_id
													? `Connection #${scan.m365_connection_id}`
													: "-")}
										</td>
										<td className="px-5 py-4 text-(--text-primary) text-sm border-b border-(--border-color)]">
											{(() => {
												const dateString =
													scan.started_at ||
													scan.created_at;
												if (!dateString) return "-";
												const dt =
													formatDate(dateString);
												return (
													<div className="flex flex-col gap-0.5 leading-tight">
														<div className="text-(--text-primary) font-semibold text-[13px]">
															{dt.date}
														</div>
														<div className="text-(--text-tertiary) text-xs">
															{dt.time}
														</div>
													</div>
												);
											})()}
										</td>
										<td className="px-5 py-4 text-(--text-primary) text-sm border-b border-(--border-color)]">
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
												className="flex items-center gap-2 rounded-lg font-medium cursor-pointer [transition:all_0.3s_ease] border-none outline-none text-[#ef4444] px-2.5 py-1.5 text-[13px]"
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
