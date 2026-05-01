import React, { useEffect, useMemo, useState } from "react";
import ComplianceChart from "../components/ComplianceChart";
import Dropdown from "../components/Dropdown";
import { useNavigate } from "react-router-dom";
import {
  CheckCircle2,
  AlertTriangle,
  Clock3,
  Shield,
  Sun,
  Moon,
} from "lucide-react";
import { Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
  getBenchmarks,
  getConnections,
  getScans,
  getScan,
} from "../api/client";
import { formatDateTimePartsAEST } from "../utils/helpers";

type ChartType = "doughnut" | "pie" | "bar";

type DashboardProps = {
  sidebarWidth?: number;
  isDarkMode: boolean;
  onThemeToggle: React.ChangeEventHandler<HTMLInputElement>;
};

type ApiConnection = {
  id: number | string;
  name?: string | null;
};

type ApiBenchmark = {
  platform?: string | null;
  framework?: string | null;
  slug?: string | null;
  version?: string | null;
  name?: string | null;
};

type ApiScanSummary = {
  id: number;
  status?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  framework?: string | null;
  benchmark?: string | null;
  version?: string | null;
  m365_connection_id?: number | string | null;
  connection_name?: string | null;
  passed_count?: number | string | null;
  failed_count?: number | string | null;
  error_count?: number | string | null;
  skipped_count?: number | string | null;
  total_controls?: number | string | null;
};

type ApiScanResultItem = {
  control_id?: string | number | null;
  status?: string | null;
  message?: string | null;
};

type ApiScanDetail = {
  id: number;
  results?: ApiScanResultItem[] | null;
};

function getErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "message" in err) {
    const m = (err as { message?: unknown }).message;
    if (typeof m === "string" && m.trim()) return m;
  }
  return "Unexpected error";
}

export default function Dashboard({
  sidebarWidth = 220,
  isDarkMode,
  onThemeToggle,
}: DashboardProps) {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [scans, setScans] = useState<ApiScanSummary[]>([]);
  const [connections, setConnections] = useState<ApiConnection[]>([]);
  const [benchmarks, setBenchmarksState] = useState<ApiBenchmark[]>([]);

  const [scanDetailsById, setScanDetailsById] = useState<
    Record<number, ApiScanDetail>
  >({});
  const [scanDetailsError, setScanDetailsError] = useState<string | null>(null);

  const chartTypeOptions = [
    { value: "doughnut", label: "Doughnut Chart" },
    { value: "pie", label: "Pie Chart" },
    { value: "bar", label: "Compliance Trend (Bar)" },
  ];

  const [selectedChartType, setSelectedChartType] =
    useState<ChartType>("doughnut");
  const [selectedConnectionId, setSelectedConnectionId] =
    useState<string>("all");
  const [selectedBenchmarkKey, setSelectedBenchmarkKey] =
    useState<string>("all");

  useEffect(() => {
    async function loadDashboard() {
      if (!token) return;
      setIsLoading(true);
      setError(null);

      try {
        const [scansData, connectionsData, benchmarksData] = await Promise.all([
          getScans(token),
          getConnections(token),
          getBenchmarks(token),
        ]);

        setScans((scansData as ApiScanSummary[] | null | undefined) || []);
        setConnections(
          (connectionsData as ApiConnection[] | null | undefined) || [],
        );
        setBenchmarksState(
          (benchmarksData as ApiBenchmark[] | null | undefined) || [],
        );

        const completed = (
          (scansData as ApiScanSummary[] | null | undefined) || []
        ).filter((s) => s.status === "completed");
        const latestCompleted = completed.length > 0 ? completed[0] : null;

        if (latestCompleted) {
          if (latestCompleted.m365_connection_id) {
            setSelectedConnectionId(String(latestCompleted.m365_connection_id));
          }
          if (
            latestCompleted.framework &&
            latestCompleted.benchmark &&
            latestCompleted.version
          ) {
            setSelectedBenchmarkKey(
              `${latestCompleted.framework}|${latestCompleted.benchmark}|${latestCompleted.version}`,
            );
          }
        }
      } catch (err: unknown) {
        setError(getErrorMessage(err) || "Failed to load dashboard");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [token]);

  const benchmarkOptions = useMemo(() => {
    const m365 = (benchmarks || []).filter(
      (b) => String(b.platform || "").toLowerCase() === "m365",
    );

    const opts = m365.map((b) => ({
      value: `${b.framework || ""}|${b.slug || ""}|${b.version || ""}`,
      label: `${b.name || "Benchmark"} (${b.version || "—"})`,
    }));

    return [{ value: "all", label: "All benchmarks" }, ...opts];
  }, [benchmarks]);

  const connectionOptions = useMemo(() => {
    const opts = (connections || []).map((c) => ({
      value: String(c.id),
      label: c.name || `Connection #${c.id}`,
    }));

    return [{ value: "all", label: "All connections" }, ...opts];
  }, [connections]);

  const filteredScans = useMemo(() => {
    let out = scans || [];

    if (selectedConnectionId !== "all") {
      out = out.filter(
        (s) => String(s.m365_connection_id || "") === selectedConnectionId,
      );
    }

    if (selectedBenchmarkKey !== "all") {
      out = out.filter(
        (s) =>
          `${s.framework}|${s.benchmark}|${s.version}` === selectedBenchmarkKey,
      );
    }

    return out;
  }, [scans, selectedConnectionId, selectedBenchmarkKey]);

  const latestRelevantScan = useMemo(() => {
    if (!filteredScans || filteredScans.length === 0) return null;
    const completed = filteredScans.filter((s) => s.status === "completed");
    if (completed.length > 0) return completed[0];
    return filteredScans[0];
  }, [filteredScans]);

  const chartModel = useMemo<{
    chartType: ChartType;
    labels: string[];
    values: number[];
  }>(() => {
    const s = latestRelevantScan;
    const passed = Number(s?.passed_count || 0);
    const failed = Number(s?.failed_count || 0);
    const errors = Number(s?.error_count || 0);
    const skipped = Number(s?.skipped_count || 0);

    if (selectedChartType === "bar") {
      const completed = (filteredScans || [])
        .filter((x) => String(x.status || "").toLowerCase() === "completed")
        .slice(0, 8)
        .slice()
        .reverse();

      const labels = completed.map((x) => `#${x.id}`);
      const values = completed.map((x) => {
        const pass = Number(x.passed_count || 0);
        const fail = Number(x.failed_count || 0);
        const evaluated = pass + fail;
        return evaluated > 0 ? Math.round((pass / evaluated) * 100) : 0;
      });

      return { chartType: "bar", labels, values };
    }

    const labels = ["Pass", "Fail"];
    const values = [passed, failed];

    if (errors > 0) {
      labels.push("Error");
      values.push(errors);
    }

    if (skipped > 0) {
      labels.push("Skipped");
      values.push(skipped);
    }

    return { chartType: selectedChartType, labels, values };
  }, [selectedChartType, latestRelevantScan, filteredScans]);

  const latestScanDetails = useMemo(() => {
    const id = latestRelevantScan?.id;
    if (!id) return null;
    return scanDetailsById[id] || null;
  }, [latestRelevantScan?.id, scanDetailsById]);

  useEffect(() => {
    async function loadScanDetails() {
      if (!token) return;
      const id = latestRelevantScan?.id;
      if (!id) return;

      if (scanDetailsById[id]) return;

      setScanDetailsError(null);

      try {
        const detail = (await getScan(token, id)) as ApiScanDetail;
        setScanDetailsById((prev) => ({ ...prev, [id]: detail }));
      } catch (err: unknown) {
        setScanDetailsError(
          getErrorMessage(err) || "Failed to load scan details",
        );
      }
    }

    loadScanDetails();
  }, [token, latestRelevantScan?.id]);

  const summary = useMemo(() => {
    const s = latestRelevantScan;
    const hasScan = Boolean(s);
    const total = s ? Number(s.total_controls || 0) : 0;
    const passed = s ? Number(s.passed_count || 0) : 0;
    const failed = s ? Number(s.failed_count || 0) : 0;
    const errors = s ? Number(s.error_count || 0) : 0;
    const skipped = s ? Number(s.skipped_count || 0) : 0;
    const evaluated = passed + failed;
    const pending = Math.max(0, total - evaluated - errors - skipped);
    const hasTotal = total > 0;

    const formatCount = (value: unknown) => {
      const num = Number(value);
      return Number.isFinite(num) ? num.toLocaleString() : "—";
    };

    const compliancePct =
      evaluated > 0 ? Math.round((passed / evaluated) * 100) : null;
    const complianceTone = hasScan ? "good" : "neutral";
    const failedTone = failed > 0 ? "bad" : hasTotal ? "good" : "neutral";

    const connectionLabel =
      s?.connection_name ||
      (s?.m365_connection_id ? `Connection #${s.m365_connection_id}` : "—");

    const isCompleted = String(s?.status || "").toLowerCase() === "completed";
    const lastScanLabel =
      (isCompleted
        ? s?.finished_at || s?.started_at
        : s?.started_at || s?.finished_at) || null;

    const dt = lastScanLabel
      ? formatDateTimePartsAEST(lastScanLabel)
      : { date: "-", time: "-" };

    const lastTime = dt.time !== "-" ? dt.time : "—";
    const lastDate = dt.date !== "-" ? dt.date : "—";

    const subtitle = !hasScan
      ? "No scans yet"
      : `${isCompleted ? "Latest completed scan" : "Latest scan"}${
          hasTotal ? ` • ${formatCount(evaluated)} evaluated` : ""
        }`;

    const kpis = [
      {
        label:
          compliancePct === null
            ? "Compliance —"
            : `Compliance ${compliancePct}%`,
        tone: complianceTone,
        icon: CheckCircle2,
      },
      {
        label: hasTotal ? `${formatCount(failed)} failed` : "Failed —",
        tone: failedTone,
        icon: AlertTriangle,
      },
      {
        label: hasTotal ? `${formatCount(total)} total` : "Total —",
        tone: "neutral",
        icon: Shield,
      },
      {
        label: `Updated ${lastTime}`,
        tone: "neutral",
        icon: Clock3,
      },
    ];

    const groups = [
      {
        title: "Evaluation",
        items: [
          {
            label: "Evaluated",
            value: hasTotal
              ? `${formatCount(evaluated)} of ${formatCount(total)}`
              : "—",
          },
          { label: "Passed", value: hasTotal ? formatCount(passed) : "—" },
          { label: "Failed", value: hasTotal ? formatCount(failed) : "—" },
        ],
      },
      {
        title: "Quality",
        items: [
          { label: "Errors", value: hasTotal ? formatCount(errors) : "—" },
          { label: "Skipped", value: hasTotal ? formatCount(skipped) : "—" },
          { label: "Pending", value: hasTotal ? formatCount(pending) : "—" },
        ],
      },
      {
        title: "Context",
        items: [
          { label: "Connection", value: hasScan ? connectionLabel : "—" },
          { label: "Date", value: hasScan ? lastDate : "—" },
        ],
      },
    ]
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => item.value !== "—"),
      }))
      .filter((group) => group.items.length > 0);

    return { subtitle, kpis, groups };
  }, [latestRelevantScan]);

  const nextFixes = useMemo(() => {
    const results = latestScanDetails?.results || [];
    const failed = results.filter(
      (r) => (r?.status || "").toLowerCase() === "failed",
    );
    const errors = results.filter(
      (r) => (r?.status || "").toLowerCase() === "error",
    );

    const byControlId = (a: ApiScanResultItem, b: ApiScanResultItem) =>
      String(a?.control_id || "").localeCompare(
        String(b?.control_id || ""),
        undefined,
        {
          numeric: true,
        },
      );

    return {
      failedCount: failed.length,
      errorCount: errors.length,
      topItems: failed
        .slice()
        .sort(byControlId)
        .slice(0, 6)
        .concat(errors.slice().sort(byControlId).slice(0, 2)),
    };
  }, [latestScanDetails]);

  const recentScans = useMemo(() => {
    return (filteredScans || []).slice(0, 6);
  }, [filteredScans]);

  function statusTone(status: unknown) {
    switch (String(status || "").toLowerCase()) {
      case "completed":
        return "success";
      case "failed":
        return "error";
      case "running":
        return "running";
      default:
        return "pending";
    }
  }

  function summaryChipClasses(tone: string) {
    const base =
      "inline-flex items-center gap-[6px] whitespace-nowrap rounded-full border px-[10px] py-[6px] text-[13px] font-semibold leading-none";
    switch (tone) {
      case "good":
        return `${base} border-[rgba(16,185,129,0.3)] bg-[rgba(16,185,129,0.12)] text-[#10b981]`;
      case "warn":
        return `${base} border-[rgba(249,115,22,0.3)] bg-[rgba(249,115,22,0.12)] text-[#f97316]`;
      case "bad":
        return `${base} border-[rgba(239,68,68,0.3)] bg-[rgba(239,68,68,0.12)] text-[#ef4444]`;
      default:
        return isDarkMode
          ? `${base} border-[rgba(59,130,246,0.16)] bg-[rgba(30,41,59,0.78)] text-white`
          : `${base} border-[#e2e8f0] bg-[#e2e8f0] text-[#1e293b]`;
    }
  }

  function statusPillClasses(status: unknown) {
    const base =
      "inline-flex items-center justify-center rounded-full border px-[10px] py-[4px] text-[11px] font-bold tracking-[0.3px]";
    switch (statusTone(status)) {
      case "success":
        return `${base} border-[rgba(16,185,129,0.35)] bg-[rgba(16,185,129,0.12)] text-[#10b981]`;
      case "error":
        return `${base} border-[rgba(239,68,68,0.35)] bg-[rgba(239,68,68,0.12)] text-[#ef4444]`;
      case "running":
        return `${base} border-[rgba(59,130,246,0.35)] bg-[rgba(59,130,246,0.12)] text-[#93c5fd]`;
      default:
        return `${base} border-[rgba(249,115,22,0.35)] bg-[rgba(249,115,22,0.12)] text-[#f97316]`;
    }
  }

  function resultPillClasses(tone: "good" | "bad" | "warn") {
    const base =
      "inline-flex items-center rounded-full border px-[8px] py-[3px] text-[12px]";
    if (tone === "good") {
      return `${base} border-[rgba(16,185,129,0.35)] bg-[rgba(16,185,129,0.10)] text-[#10b981]`;
    }
    if (tone === "bad") {
      return `${base} border-[rgba(239,68,68,0.35)] bg-[rgba(239,68,68,0.10)] text-[#ef4444]`;
    }
    return `${base} border-[rgba(249,115,22,0.35)] bg-[rgba(249,115,22,0.10)] text-[#f97316]`;
  }

  const pageBg = isDarkMode ? "text-white" : "bg-[#f8fafc] text-[#1e293b]";

  const panelBase = isDarkMode
    ? "border border-[rgba(59,130,246,0.16)] bg-[rgba(15,23,42,0.72)]"
    : "border border-[#e2e8f0] bg-white";

  const tertiaryPanel = isDarkMode
    ? "bg-[rgba(30,41,59,0.78)]"
    : "bg-[#e2e8f0]";

  const mutedPanel = isDarkMode
    ? "border-[rgba(59,130,246,0.16)] bg-[rgba(30,41,59,0.78)]"
    : "border-[#e2e8f0] bg-[#e2e8f0]";

  const textPrimary = isDarkMode ? "text-white" : "text-[#1e293b]";
  const textSecondary = isDarkMode ? "text-[#cbd5e1]" : "text-[#64748b]";
  const textTertiary = isDarkMode ? "text-[#94a3b8]" : "text-[#94a3b8]";
  const hoverRow = isDarkMode
    ? "hover:bg-[rgba(30,41,59,0.55)]"
    : "hover:bg-[#f8fafc]";

  const secondaryButton = isDarkMode
    ? "border border-[rgba(59,130,246,0.16)] bg-[rgba(30,41,59,0.78)] text-white hover:bg-[rgba(51,65,85,0.9)]"
    : "border border-[#e2e8f0] bg-[#e2e8f0] text-[#1e293b] hover:bg-[#dbe4ee]";

  const primaryButton =
    "border border-[rgba(59,130,246,0.35)] bg-[#3b82f6] text-white shadow-[0_8px_24px_rgba(59,130,246,0.22)] hover:-translate-y-[1px] hover:brightness-105 hover:border-[rgba(59,130,246,0.6)] hover:shadow-[0_12px_30px_rgba(59,130,246,0.35)]";

  const handleRunNewScan = () => {
    const preselect = {
      m365_connection_id:
        selectedConnectionId !== "all"
          ? Number(selectedConnectionId)
          : undefined,
      benchmark_key:
        selectedBenchmarkKey !== "all" ? selectedBenchmarkKey : undefined,
    };
    navigate("/scans", { state: { openNewScan: true, preselect } });
  };

  const handleExportReport = () => {
    if (!latestRelevantScan?.id) return;
    navigate(`/scans/${latestRelevantScan.id}`);
  };

  const handleEvidenceScanner = () => {
    navigate("/evidence-scanner");
  };

  return (
    <div
      className={`${pageBg} min-h-screen px-6 py-5 transition-colors duration-300`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: "margin-left 0.4s ease, width 0.4s ease",
        background: isDarkMode
          ? "radial-gradient(1200px 650px at 280px 0px, rgba(59, 130, 246, 0.22), transparent 60%), radial-gradient(900px 540px at calc(100% - 260px) 80px, rgba(16, 185, 129, 0.14), transparent 65%), #0a1628"
          : undefined,
      }}
    >
      <div className="mx-auto flex max-w-330 flex-col gap-6">
        <div className="mb-0 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div className="flex items-center gap-4">
            <div
              className={`flex h-14 w-14 items-center justify-center rounded-[14px] ${panelBase}`}
            >
              <picture>
                <source srcSet="/AutoAudit.webp" type="image/webp" />
                <img
                  src="/AutoAudit.png"
                  alt="AutoAudit Logo"
                  className="h-14 w-14 rounded-xl object-contain"
                  loading="lazy"
                  width="56"
                  height="56"
                />
              </picture>
            </div>

            <div>
              <h1 className={`m-0 text-[24px] font-bold ${textPrimary}`}>
                AutoAudit
              </h1>
              <p className={`m-0 text-[14px] ${textSecondary}`}>
                Microsoft 365 Compliance Platform
              </p>
            </div>
          </div>

          <div
            className="flex items-center gap-3 self-end md:self-auto"
            role="group"
            aria-label="Theme toggle"
          >
            <Sun size={18} className={textTertiary} />

            <label className="relative inline-block h-6.5 w-12.5">
              <input
                type="checkbox"
                checked={isDarkMode}
                onChange={onThemeToggle}
                aria-label="Toggle theme"
                className="peer sr-only"
              />
              <span
                className={`absolute inset-0 cursor-pointer rounded-[26px] transition duration-300 ${
                  isDarkMode ? "bg-[#3b82f6]" : "bg-[#ccc]"
                } after:absolute after:bottom-0.75 after:left-0.75 after:h-5 after:w-5 after:rounded-full after:bg-white after:transition after:duration-300 after:content-[''] peer-checked:after:translate-x-6`}
              />
            </label>

            <Moon size={18} className={textTertiary} />
          </div>
        </div>

        <div
          className={`relative z-50 grid items-center gap-4 overflow-visible rounded-xl px-6 py-4 shadow-[0_0_0_1px_rgba(59,130,246,0.06)] md:grid-cols-[minmax(0,1fr)_auto] ${panelBase}`}
        >
          <div className="flex min-w-0 flex-1 flex-wrap items-center gap-3 overflow-visible">
            <span className={`text-[14px] font-medium ${textPrimary}`}>
              Connection
            </span>
            <Dropdown
              value={selectedConnectionId}
              onChange={setSelectedConnectionId}
              options={connectionOptions}
              isDarkMode={isDarkMode}
            />

            <span className={`text-[14px] font-medium ${textPrimary}`}>
              Benchmark
            </span>
            <Dropdown
              value={selectedBenchmarkKey}
              onChange={setSelectedBenchmarkKey}
              options={benchmarkOptions}
              isDarkMode={isDarkMode}
            />
          </div>

          <div className="flex flex-wrap items-center justify-end gap-3 max-sm:w-full max-sm:flex-col">
            <button
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-[14px] font-medium transition ${secondaryButton}`}
              onClick={handleExportReport}
              disabled={!latestRelevantScan?.id}
            >
              Export Report
            </button>

            <button
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-[14px] font-medium transition ${secondaryButton}`}
              onClick={handleEvidenceScanner}
            >
              Evidence Scanner
            </button>

            <button
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-[14px] font-semibold transition ${primaryButton}`}
              onClick={handleRunNewScan}
            >
              Run New Scan
            </button>
          </div>
        </div>

        {isLoading && (
          <div
            className={`flex items-center gap-2.5 rounded-xl px-4 py-3 ${panelBase}`}
          >
            <Loader2 size={18} className="animate-spin" />
            <span>Loading latest results…</span>
          </div>
        )}

        {error && !isLoading && (
          <div
            className={`flex items-center gap-2.5 rounded-xl border-l-4 px-4 py-3 ${
              isDarkMode
                ? "border border-[rgba(59,130,246,0.16)] border-l-[#ef4444] bg-[rgba(15,23,42,0.72)] text-white"
                : "border border-[#e2e8f0] border-l-[#ef4444] bg-white text-[#1e293b]"
            }`}
          >
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div
          className={`flex flex-col gap-3 rounded-2xl px-5.5 py-4.5 shadow-[0_0_0_1px_rgba(59,130,246,0.05)] ${panelBase}`}
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h3 className={`m-0 text-[18px] font-bold ${textPrimary}`}>
                Scan Snapshot
              </h3>
              <p className={`mt-1 text-[13px] ${textSecondary}`}>
                {summary.subtitle}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {summary.kpis.map((kpi) => {
                const Icon = kpi.icon;
                return (
                  <span
                    key={kpi.label}
                    className={summaryChipClasses(kpi.tone)}
                  >
                    <Icon size={14} strokeWidth={2} aria-hidden="true" />
                    {kpi.label}
                  </span>
                );
              })}
            </div>
          </div>

          {summary.groups.length > 0 && (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
              {summary.groups.map((group) => (
                <div
                  key={group.title}
                  className={`grid gap-2 rounded-xl border px-3 py-2.5 ${mutedPanel}`}
                >
                  <div
                    className={`text-[11px] font-bold uppercase tracking-[0.6px] ${textTertiary}`}
                  >
                    {group.title}
                  </div>

                  <div className="grid gap-1.5">
                    {group.items.map((item) => (
                      <div
                        key={item.label}
                        className="flex items-center justify-between gap-2.5 text-[13px]"
                      >
                        <span
                          className={`whitespace-nowrap font-medium ${textSecondary}`}
                        >
                          {item.label}
                        </span>
                        <span
                          className={`max-w-45 overflow-hidden text-ellipsis whitespace-nowrap text-right font-semibold tabular-nums ${textPrimary}`}
                        >
                          {item.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 items-start gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <div className="flex min-w-0 flex-col gap-6">
            <div
              className={`relative flex min-h-0 flex-col gap-4 overflow-visible rounded-xl p-6 shadow-[0_0_0_1px_rgba(59,130,246,0.05)] ${panelBase}`}
            >
              <div className="relative z-5 flex items-center justify-between">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <span
                    className={`inline-flex h-6 w-6 items-center justify-center rounded-md ${
                      isDarkMode
                        ? "bg-[rgba(100,116,139,0.2)] text-[#94a3b8]"
                        : "bg-[#e2e8f0] text-[#64748b]"
                    }`}
                  >
                    ▷
                  </span>
                  <h4 className={`m-0 text-[14px] font-medium ${textPrimary}`}>
                    Scan Results
                  </h4>
                </div>
                <Dropdown
                  value={selectedChartType}
                  onChange={(value) => setSelectedChartType(value as ChartType)}
                  options={chartTypeOptions}
                  isDarkMode={isDarkMode}
                />
              </div>

              <div className="flex justify-center items-center relative z-1 min-h-75 w-full overflow-hidden">
                <ComplianceChart
                  isDarkMode={isDarkMode}
                  sidebarWidth={sidebarWidth}
                />
              </div>
            </div>

            <div className={`rounded-xl p-4.5 ${panelBase}`}>
              <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className={`m-0 text-[16px] font-bold ${textPrimary}`}>
                    Recent Scans
                  </h3>
                  <p className={`mt-1 text-[12px] ${textSecondary}`}>
                    Latest activity for your selected connection/benchmark
                  </p>
                </div>

                <button
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-[14px] font-medium transition ${secondaryButton}`}
                  onClick={() => navigate("/scans")}
                >
                  Open Scans
                </button>
              </div>

              {recentScans.length === 0 ? (
                <div
                  className={`flex flex-col items-start justify-between gap-3 rounded-[10px] border px-3 py-3.5 sm:flex-row sm:items-center ${mutedPanel}`}
                >
                  <p className={`m-0 text-[13px] ${textSecondary}`}>
                    No scans found for the current filters.
                  </p>

                  <button
                    className={`flex items-center gap-2 rounded-lg px-4 py-2 text-[14px] font-semibold transition ${primaryButton}`}
                    onClick={handleRunNewScan}
                  >
                    Run a Scan
                  </button>
                </div>
              ) : (
                <div
                  className={`overflow-hidden rounded-[10px] border ${
                    isDarkMode
                      ? "border-[rgba(59,130,246,0.16)]"
                      : "border-[#e2e8f0]"
                  }`}
                >
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className={tertiaryPanel}>
                          <th
                            className={`border-b px-3.5 py-3 text-left text-[12px] font-bold ${
                              isDarkMode
                                ? "border-[rgba(59,130,246,0.16)] text-[#cbd5e1]"
                                : "border-[#e2e8f0] text-[#64748b]"
                            }`}
                          >
                            Status
                          </th>
                          <th
                            className={`border-b px-3.5 py-3 text-left text-[12px] font-bold ${
                              isDarkMode
                                ? "border-[rgba(59,130,246,0.16)] text-[#cbd5e1]"
                                : "border-[#e2e8f0] text-[#64748b]"
                            }`}
                          >
                            Started
                          </th>
                          <th
                            className={`border-b px-3.5 py-3 text-left text-[12px] font-bold ${
                              isDarkMode
                                ? "border-[rgba(59,130,246,0.16)] text-[#cbd5e1]"
                                : "border-[#e2e8f0] text-[#64748b]"
                            }`}
                          >
                            Results
                          </th>
                          <th
                            className={`border-b px-3.5 py-3 text-right text-[12px] font-bold ${
                              isDarkMode
                                ? "border-[rgba(59,130,246,0.16)] text-[#cbd5e1]"
                                : "border-[#e2e8f0] text-[#64748b]"
                            }`}
                          >
                            Open
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        {recentScans.map((s) => {
                          const dt = formatDateTimePartsAEST(
                            s.started_at || s.finished_at,
                          );
                          const passed = Number(s.passed_count || 0);
                          const failed = Number(s.failed_count || 0);
                          const errors = Number(s.error_count || 0);

                          return (
                            <tr key={s.id} className={hoverRow}>
                              <td
                                className={`border-b px-3.5 py-3 text-[13px] ${
                                  isDarkMode
                                    ? "border-[rgba(59,130,246,0.16)] text-white"
                                    : "border-[#e2e8f0] text-[#1e293b]"
                                }`}
                              >
                                <span className={statusPillClasses(s.status)}>
                                  {String(s.status || "pending").toUpperCase()}
                                </span>
                              </td>

                              <td
                                className={`border-b px-3.5 py-3 text-[13px] ${
                                  isDarkMode
                                    ? "border-[rgba(59,130,246,0.16)] text-white"
                                    : "border-[#e2e8f0] text-[#1e293b]"
                                }`}
                              >
                                <div className="flex flex-col gap-0.5 leading-[1.2]">
                                  <div className="text-[12px] font-bold">
                                    {dt.date}
                                  </div>
                                  <div
                                    className={`text-[12px] ${textTertiary}`}
                                  >
                                    {dt.time}
                                  </div>
                                </div>
                              </td>

                              <td
                                className={`border-b px-3.5 py-3 text-[13px] ${
                                  isDarkMode
                                    ? "border-[rgba(59,130,246,0.16)] text-white"
                                    : "border-[#e2e8f0] text-[#1e293b]"
                                }`}
                              >
                                <div className="flex flex-wrap gap-2">
                                  <span className={resultPillClasses("good")}>
                                    {passed} pass
                                  </span>
                                  <span className={resultPillClasses("bad")}>
                                    {failed} fail
                                  </span>
                                  {errors > 0 && (
                                    <span className={resultPillClasses("warn")}>
                                      {errors} err
                                    </span>
                                  )}
                                </div>
                              </td>

                              <td
                                className={`border-b px-3.5 py-3 text-right text-[13px] ${
                                  isDarkMode
                                    ? "border-[rgba(59,130,246,0.16)] text-white"
                                    : "border-[#e2e8f0] text-[#1e293b]"
                                }`}
                              >
                                <button
                                  className={`rounded-lg border px-2.5 py-1.5 font-semibold transition ${
                                    isDarkMode
                                      ? "border-[rgba(59,130,246,0.16)] bg-transparent text-white hover:border-[rgba(59,130,246,0.45)] hover:bg-[rgba(59,130,246,0.10)]"
                                      : "border-[#e2e8f0] bg-transparent text-[#1e293b] hover:border-[#93c5fd] hover:bg-[#eff6ff]"
                                  }`}
                                  onClick={() => navigate(`/scans/${s.id}`)}
                                  type="button"
                                >
                                  View
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <div
              className={`rounded-xl border-l-4 p-6 ${
                isDarkMode
                  ? "border border-[rgba(59,130,246,0.16)] border-l-[rgba(59,130,246,0.4)] bg-[rgba(15,23,42,0.72)]"
                  : "border border-[#e2e8f0] border-l-[rgba(59,130,246,0.4)] bg-white"
              }`}
            >
              <div className="mb-3.5 flex min-w-0 items-center justify-between">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <span
                    className={`inline-flex h-6 w-6 items-center justify-center rounded-full ${
                      isDarkMode
                        ? "bg-[rgba(148,163,184,0.15)] text-[rgba(148,163,184,0.95)]"
                        : "bg-[#e2e8f0] text-[#64748b]"
                    }`}
                    aria-hidden="true"
                  >
                    <AlertTriangle size={16} strokeWidth={2.2} />
                  </span>

                  <h4 className={`m-0 text-[14px] font-medium ${textPrimary}`}>
                    What you should change next
                  </h4>
                </div>

                <span
                  className={
                    isDarkMode
                      ? "text-[24px] font-bold text-[#94a3b8]"
                      : "text-[24px] font-bold text-[#64748b]"
                  }
                >
                  {latestRelevantScan
                    ? Number(latestRelevantScan.failed_count || 0) +
                      Number(latestRelevantScan.error_count || 0)
                    : "—"}
                </span>
              </div>

              <p className={`m-0 text-[12px] leading-[1.4] ${textSecondary}`}>
                Top failing controls from the latest scan
              </p>

              {scanDetailsError ? (
                <div className={`mt-3 rounded-[10px] border p-3 ${mutedPanel}`}>
                  <p
                    className={`m-0 text-[13px] leading-[1.4] ${textSecondary}`}
                  >
                    {scanDetailsError}
                  </p>
                </div>
              ) : !latestRelevantScan?.id ? (
                <div className={`mt-3 rounded-[10px] border p-3 ${mutedPanel}`}>
                  <p
                    className={`m-0 text-[13px] leading-[1.4] ${textSecondary}`}
                  >
                    No scan selected.
                  </p>
                </div>
              ) : !latestScanDetails ? (
                <div className={`mt-3 rounded-[10px] border p-3 ${mutedPanel}`}>
                  <p
                    className={`m-0 text-[13px] leading-[1.4] ${textSecondary}`}
                  >
                    Loading control results…
                  </p>
                </div>
              ) : nextFixes.topItems.length === 0 ? (
                <div className={`mt-3 rounded-[10px] border p-3 ${mutedPanel}`}>
                  <p
                    className={`m-0 text-[13px] leading-[1.4] ${textSecondary}`}
                  >
                    No failed/error controls in this scan.
                  </p>
                </div>
              ) : (
                <div className="mt-3 flex flex-col gap-2.5">
                  {nextFixes.topItems.map((r, idx) => (
                    <button
                      key={`${r.control_id || idx}`}
                      className={`grid w-full grid-cols-[72px_minmax(0,1fr)] items-start gap-2.5 rounded-xl border px-3 py-2.5 text-left transition ${
                        isDarkMode
                          ? "border-[rgba(59,130,246,0.16)] bg-[rgba(30,41,59,0.78)] text-white hover:border-[rgba(59,130,246,0.45)] hover:bg-[rgba(59,130,246,0.10)]"
                          : "border-[#e2e8f0] bg-[#e2e8f0] text-[#1e293b] hover:border-[#93c5fd] hover:bg-[#eff6ff]"
                      }`}
                      onClick={() =>
                        latestRelevantScan?.id &&
                        navigate(`/scans/${latestRelevantScan.id}`)
                      }
                      type="button"
                    >
                      <span className="text-[12px] font-extrabold tabular-nums text-[rgba(147,197,253,0.95)]">
                        {r.control_id || "—"}
                      </span>

                      <span
                        className={`overflow-hidden text-[12px] leading-[1.35] ${textSecondary}`}
                        style={{
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                        }}
                      >
                        {r.message || "No message provided"}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
