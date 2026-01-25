import React, { useEffect, useMemo, useState } from "react";
import "./Dashboard.css";
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
import { getBenchmarks, getConnections, getScans, getScan } from "../api/client";
import { formatDateTimePartsAEST } from "../utils/helpers";

export default function Dashboard({ sidebarWidth = 220, isDarkMode, onThemeToggle }) {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [scans, setScans] = useState([]);
  const [connections, setConnections] = useState([]);
  const [benchmarks, setBenchmarksState] = useState([]);

  const [scanDetailsById, setScanDetailsById] = useState({});
  const [scanDetailsError, setScanDetailsError] = useState(null);

  const chartTypeOptions = [
    { value: 'doughnut', label: 'Doughnut Chart' },
    { value: 'pie', label: 'Pie Chart' },
    { value: 'bar', label: 'Compliance Trend (Bar)' },
  ];
    
  const [selectedChartType, setSelectedChartType] = useState('doughnut');
  const [selectedConnectionId, setSelectedConnectionId] = useState('all');
  const [selectedBenchmarkKey, setSelectedBenchmarkKey] = useState('all');

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
        setScans(scansData || []);
        setConnections(connectionsData || []);
        setBenchmarksState(benchmarksData || []);

        // Prefer the latest completed scan as the default context.
        const completed = (scansData || []).filter(s => s.status === 'completed');
        const latestCompleted = completed.length > 0 ? completed[0] : null; // API sorts started_at desc
        if (latestCompleted) {
          if (latestCompleted.m365_connection_id) {
            setSelectedConnectionId(String(latestCompleted.m365_connection_id));
          }
          if (latestCompleted.framework && latestCompleted.benchmark && latestCompleted.version) {
            setSelectedBenchmarkKey(`${latestCompleted.framework}|${latestCompleted.benchmark}|${latestCompleted.version}`);
          }
        }
      } catch (err) {
        setError(err?.message || 'Failed to load dashboard');
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [token]);

  const benchmarkOptions = useMemo(() => {
    const m365 = (benchmarks || []).filter(b => String(b.platform || '').toLowerCase() === 'm365');
    const opts = m365.map(b => ({
      value: `${b.framework}|${b.slug}|${b.version}`,
      label: `${b.name} (${b.version})`,
    }));
    return [{ value: 'all', label: 'All benchmarks' }, ...opts];
  }, [benchmarks]);

  const connectionOptions = useMemo(() => {
    const opts = (connections || []).map(c => ({ value: String(c.id), label: c.name || `Connection #${c.id}` }));
    return [{ value: 'all', label: 'All connections' }, ...opts];
  }, [connections]);

  const filteredScans = useMemo(() => {
    let out = scans || [];
    if (selectedConnectionId !== 'all') {
      out = out.filter(s => String(s.m365_connection_id || '') === selectedConnectionId);
    }
    if (selectedBenchmarkKey !== 'all') {
      out = out.filter(s => `${s.framework}|${s.benchmark}|${s.version}` === selectedBenchmarkKey);
    }
    return out;
  }, [scans, selectedConnectionId, selectedBenchmarkKey]);

  const latestRelevantScan = useMemo(() => {
    if (!filteredScans || filteredScans.length === 0) return null;
    const completed = filteredScans.filter(s => s.status === 'completed');
    if (completed.length > 0) return completed[0];
    return filteredScans[0];
  }, [filteredScans]);

  const chartModel = useMemo(() => {
    const s = latestRelevantScan;
    const passed = Number(s?.passed_count || 0);
    const failed = Number(s?.failed_count || 0);
    const errors = Number(s?.error_count || 0);
    const issues = failed + errors;

    if (selectedChartType === 'bar') {
      const completed = (filteredScans || [])
        .filter(x => String(x.status || '').toLowerCase() === 'completed')
        .slice(0, 8)
        .slice()
        .reverse();

      const labels = completed.map(x => `#${x.id}`);
      const values = completed.map(x => {
        const total = Number(x.total_controls || 0);
        const pass = Number(x.passed_count || 0);
        return total > 0 ? Math.round((pass / total) * 100) : 0;
      });

      return { chartType: 'bar', labels, values };
    }

    // Default: issues vs pass (doughnut or pie)
    return { chartType: selectedChartType, labels: ['Issues', 'Pass'], values: [issues, passed] };
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

      // Cache scan details in-memory to avoid refetching on minor UI changes.
      if (scanDetailsById[id]) return;

      setScanDetailsError(null);
      try {
        const detail = await getScan(token, id);
        setScanDetailsById(prev => ({ ...prev, [id]: detail }));
      } catch (err) {
        setScanDetailsError(err?.message || 'Failed to load scan details');
      }
    }

    loadScanDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, latestRelevantScan?.id]);

  const stats = useMemo(() => {
    const s = latestRelevantScan;
    const total = s ? Number(s.total_controls || 0) : 0;
    const passed = s ? Number(s.passed_count || 0) : 0;
    const failed = s ? Number(s.failed_count || 0) : 0;
    const errors = s ? Number(s.error_count || 0) : 0;
    const issues = failed + errors;
    const pct = total > 0 ? Math.round((passed / total) * 100) : 0;

    const connectionLabel = s?.connection_name || (s?.m365_connection_id ? `Connection #${s.m365_connection_id}` : '—');
    const lastScanLabel = s?.finished_at || s?.started_at || null;
    const dt = lastScanLabel ? formatDateTimePartsAEST(lastScanLabel) : { date: '-', time: '-' };
    const lastText = dt.date !== '-' ? `${dt.date}, ${dt.time}` : '—';
    const benchmarkLabel = s?.benchmark && s?.version ? `${s.benchmark} ${s.version}` : '—';

    return [
      {
        label: "Compliance Score",
        value: total > 0 ? `${pct}%` : '—',
        className: "orange",
        subtitle: "Latest completed scan",
        icon: CheckCircle2,
      },
      {
        label: "Failed Controls",
        value: String(issues),
        className: "orange",
        subtitle: "Failed + errors",
        icon: AlertTriangle,
      },
      {
        label: "Last Updated",
        value: lastText,
        className: "gray",
        subtitle: connectionLabel,
        icon: Clock3,
      },
      {
        label: "Total Controls",
        value: total > 0 ? String(total) : '—',
        className: "gray",
        subtitle: benchmarkLabel,
        icon: Shield,
      },
    ];
  }, [latestRelevantScan]);

  const nextFixes = useMemo(() => {
    const results = latestScanDetails?.results || [];
    const failed = results.filter(r => (r?.status || '').toLowerCase() === 'failed');
    const errors = results.filter(r => (r?.status || '').toLowerCase() === 'error');
    const byControlId = (a, b) => String(a?.control_id || '').localeCompare(String(b?.control_id || ''), undefined, { numeric: true });
    return {
      failedCount: failed.length,
      errorCount: errors.length,
      topItems: failed.slice().sort(byControlId).slice(0, 6).concat(errors.slice().sort(byControlId).slice(0, 2)),
    };
  }, [latestScanDetails]);

  const recentScans = useMemo(() => {
    return (filteredScans || []).slice(0, 6);
  }, [filteredScans]);

  function statusTone(status) {
    switch (String(status || '').toLowerCase()) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'running';
      default:
        return 'pending';
    }
  }

  const handleRunNewScan = () => {
    const preselect = {
      m365_connection_id: selectedConnectionId !== 'all' ? Number(selectedConnectionId) : undefined,
      benchmark_key: selectedBenchmarkKey !== 'all' ? selectedBenchmarkKey : undefined,
    };
    navigate('/scans', { state: { openNewScan: true, preselect } });
  };

  const handleExportReport = () => {
    if (!latestRelevantScan?.id) return;
    navigate(`/scans/${latestRelevantScan.id}`);
  };

  const handleEvidenceScanner = () => {
    navigate("/evidence-scanner");
  };

  return (
    <div className={`dashboard ${isDarkMode ? 'dark' : 'light'}`} style={{ 
      marginLeft: `${sidebarWidth}px`, 
      width: `calc(100% - ${sidebarWidth}px)`,
      transition: 'margin-left 0.4s ease, width 0.4s ease'
    }}>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-content">
            <div className="logo-container">
              <picture>
                <source srcSet="/AutoAudit.webp" type="image/webp" />
                <img 
                  src="/AutoAudit.png" 
                  alt="AutoAudit Logo" 
                  className="logo-image"
                  loading="lazy"
                  width="56"
                  height="56"
                />
              </picture>
            </div>
            <div className="header-text">
              <h1>AutoAudit</h1>
              <p>Microsoft 365 Compliance Platform</p>
            </div>
          </div>
          
          <div className="theme-toggle" role="group" aria-label="Theme toggle">
            <Sun size={18} className={`theme-label ${!isDarkMode ? 'active' : ''}`} />
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={isDarkMode} 
                onChange={onThemeToggle}
                aria-label="Toggle theme"
              />
              <span className="slider"></span>
            </label>
            <Moon size={18} className={`theme-label ${isDarkMode ? 'active' : ''}`} />
          </div>
        </div>

        <div className="top-toolbar">
          <div className="toolbar-left">
            <span className="toolbar-label">Connection</span>
            <Dropdown
              value={selectedConnectionId}
              onChange={setSelectedConnectionId}
              options={connectionOptions}
              isDarkMode={isDarkMode}
            />
            <span className="toolbar-label">Benchmark</span>
            <Dropdown
              value={selectedBenchmarkKey}
              onChange={setSelectedBenchmarkKey}
              options={benchmarkOptions}
              isDarkMode={isDarkMode}
            />
          </div>
          
          <div className="toolbar-right">
            <button className="toolbar-button secondary" onClick={handleExportReport} disabled={!latestRelevantScan?.id}>
              Export Report
            </button>
            <button className="toolbar-button secondary" onClick={handleEvidenceScanner}>
              Evidence Scanner
            </button>
            <button className="toolbar-button primary" onClick={handleRunNewScan}>
              Run New Scan
            </button>
          </div>
        </div>

        {isLoading && (
          <div className="dashboard-banner">
            <Loader2 size={18} className="spinning" />
            <span>Loading latest results…</span>
          </div>
        )}

        {error && !isLoading && (
          <div className="dashboard-banner error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div className="stats-grid">
          {stats.map((stat, index) => {
            const Icon = stat.icon; // uppercase component so React renders the imported icon
            return (
              <div key={index} className={`stat-card ${stat.className}`}>
                <div className="stat-content">
                  <div className="stat-info">
                    <div className="stat-icon" aria-hidden="true">
                      <Icon size={18} strokeWidth={2.2} />
                    </div>
                    <div className="stat-text">
                      <p className="stat-label">{stat.label}</p>
                      <p className="stat-value">{stat.value}</p>
                      <p className="stat-subtitle">{stat.subtitle}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="main-grid">
          <div className="left-stack">
            <div className="compliance-graph-card">
              <div className="issue-header">
                <div className="issue-title">
                  <span className="issue-icon">▷</span>
                  <h4>Scan Results</h4>
                </div>
              <Dropdown
                value={selectedChartType}
                onChange={setSelectedChartType}
                options={chartTypeOptions}
              />
              </div>
              <div className="chart-surface">
                <ComplianceChart
                  chartType={chartModel.chartType}
                  labelsInput={chartModel.labels}
                  dataInput={chartModel.values}
                  isDarkMode={isDarkMode}
                />
              </div>
            </div>

            <div className="dashboard-panel">
              <div className="panel-header">
                <div className="panel-title">
                  <h3>Recent Scans</h3>
                  <p>Latest activity for your selected connection/benchmark</p>
                </div>
                <button className="toolbar-button secondary" onClick={() => navigate('/scans')}>
                  Open Scans
                </button>
              </div>

              {recentScans.length === 0 ? (
                <div className="panel-empty">
                  <p>No scans found for the current filters.</p>
                  <button className="toolbar-button primary" onClick={handleRunNewScan}>
                    Run a Scan
                  </button>
                </div>
              ) : (
                <div className="dashboard-table-wrap">
                  <table className="dashboard-table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Started</th>
                        <th>Results</th>
                        <th className="right">Open</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentScans.map(s => {
                        const dt = formatDateTimePartsAEST(s.started_at || s.finished_at);
                        const passed = Number(s.passed_count || 0);
                        const failed = Number(s.failed_count || 0);
                        const errors = Number(s.error_count || 0);
                        return (
                          <tr key={s.id}>
                            <td>
                              <span className={`status-pill ${statusTone(s.status)}`}>
                                {String(s.status || 'pending').toUpperCase()}
                              </span>
                            </td>
                            <td>
                              <div className="dt">
                                <div className="date">{dt.date}</div>
                                <div className="time">{dt.time}</div>
                              </div>
                            </td>
                            <td>
                              <div className="result-pills">
                                <span className="pill good">{passed} pass</span>
                                <span className="pill bad">{failed} fail</span>
                                {errors > 0 && <span className="pill warn">{errors} err</span>}
                              </div>
                            </td>
                            <td className="right">
                              <button className="link-button" onClick={() => navigate(`/scans/${s.id}`)} type="button">
                                View
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          <div className="issues-section">
            <div className="issue-card muted">
              <div className="issue-header">
                <div className="issue-title">
                  <span className="issue-icon" aria-hidden="true">
                    <AlertTriangle size={16} strokeWidth={2.2} />
                  </span>
                  <h4>What you should change next</h4>
                </div>
                <span className="issue-count">
                  {latestRelevantScan ? Number(latestRelevantScan.failed_count || 0) + Number(latestRelevantScan.error_count || 0) : '—'}
                </span>
              </div>
              <p className="issue-desc">Top failing controls from the latest scan</p>
              {scanDetailsError ? (
                <div className="fix-empty">
                  <p>{scanDetailsError}</p>
                </div>
              ) : !latestRelevantScan?.id ? (
                <div className="fix-empty">
                  <p>No scan selected.</p>
                </div>
              ) : !latestScanDetails ? (
                <div className="fix-empty">
                  <p>Loading control results…</p>
                </div>
              ) : nextFixes.topItems.length === 0 ? (
                <div className="fix-empty">
                  <p>No failed/error controls in this scan.</p>
                </div>
              ) : (
                <div className="fix-list">
                  {nextFixes.topItems.map((r, idx) => (
                    <button
                      key={`${r.control_id || idx}`}
                      className="fix-item"
                      onClick={() => latestRelevantScan?.id && navigate(`/scans/${latestRelevantScan.id}`)}
                      type="button"
                    >
                      <span className="fix-id">{r.control_id || '—'}</span>
                      <span className="fix-msg">{r.message || 'No message provided'}</span>
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
