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
    const skipped = Number(s?.skipped_count || 0);
    const totalControls = Number(s?.total_controls || 0);

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
        const fail = Number(x.failed_count || 0);
        // Compliance is based on determinate outcomes only.
        // Exclude errored/skipped controls from pass/fail denominator.
        const evaluated = pass + fail;
        return evaluated > 0 ? Math.round((pass / evaluated) * 100) : 0;
      });

      return { chartType: 'bar', labels, values };
    }

    // Default: Pass / Fail (+ optional Error / Skipped)
    const labels = ['Pass', 'Fail'];
    const values = [passed, failed];
    if (errors > 0) {
      labels.push('Error');
      values.push(errors);
    }
    if (skipped > 0) {
      labels.push('Skipped');
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
    const formatCount = (value) => {
      const num = Number(value);
      return Number.isFinite(num) ? num.toLocaleString() : '—';
    };

    const compliancePct = evaluated > 0 ? Math.round((passed / evaluated) * 100) : null;
    const complianceTone = compliancePct === null ? 'neutral' : compliancePct >= 85 ? 'good' : compliancePct >= 65 ? 'warn' : 'bad';
    const failedTone = failed > 0 ? 'bad' : hasTotal ? 'good' : 'neutral';

    const connectionLabel = s?.connection_name || (s?.m365_connection_id ? `Connection #${s.m365_connection_id}` : '—');
    const isCompleted = String(s?.status || '').toLowerCase() === 'completed';
    const lastScanLabel = (isCompleted ? (s?.finished_at || s?.started_at) : (s?.started_at || s?.finished_at)) || null;
    const dt = lastScanLabel ? formatDateTimePartsAEST(lastScanLabel) : { date: '-', time: '-' };
    const lastTime = dt.time !== '-' ? dt.time : '—';
    const lastDate = dt.date !== '-' ? dt.date : '—';

    const subtitle = !hasScan
      ? 'No scans yet'
      : `${isCompleted ? 'Latest completed scan' : 'Latest scan'}${hasTotal ? ` • ${formatCount(evaluated)} evaluated` : ''}`;

    const kpis = [
      {
        label: compliancePct === null ? 'Compliance —' : `Compliance ${compliancePct}%`,
        tone: complianceTone,
        icon: CheckCircle2,
      },
      {
        label: hasTotal ? `${formatCount(failed)} failed` : 'Failed —',
        tone: failedTone,
        icon: AlertTriangle,
      },
      {
        label: hasTotal ? `${formatCount(total)} total` : 'Total —',
        tone: 'neutral',
        icon: Shield,
      },
      {
        label: `Updated ${lastTime}`,
        tone: 'neutral',
        icon: Clock3,
      },
    ];

    const groups = [
      {
        title: 'Evaluation',
        items: [
          { label: 'Evaluated', value: hasTotal ? `${formatCount(evaluated)} of ${formatCount(total)}` : '—' },
          { label: 'Passed', value: hasTotal ? formatCount(passed) : '—' },
          { label: 'Failed', value: hasTotal ? formatCount(failed) : '—' },
        ],
      },
      {
        title: 'Quality',
        items: [
          { label: 'Errors', value: hasTotal ? formatCount(errors) : '—' },
          { label: 'Skipped', value: hasTotal ? formatCount(skipped) : '—' },
          { label: 'Pending', value: hasTotal ? formatCount(pending) : '—' },
        ],
      },
      {
        title: 'Context',
        items: [
          { label: 'Connection', value: hasScan ? connectionLabel : '—' },
          { label: 'Date', value: hasScan ? lastDate : '—' },
        ],
      },
    ].map(group => ({
      ...group,
      items: group.items.filter(item => item.value !== '—'),
    })).filter(group => group.items.length > 0);

    return { subtitle, kpis, groups };
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

        <div className="summary-card">
          <div className="summary-header">
            <div className="summary-title">
              <h3>Scan Snapshot</h3>
              <p>{summary.subtitle}</p>
            </div>
            <div className="summary-kpis">
              {summary.kpis.map((kpi) => {
                const Icon = kpi.icon;
                return (
                  <span key={kpi.label} className={`summary-chip ${kpi.tone}`}>
                    <Icon size={14} strokeWidth={2} aria-hidden="true" />
                    {kpi.label}
                  </span>
                );
              })}
            </div>
          </div>
          {summary.groups.length > 0 && (
            <div className="summary-groups">
              {summary.groups.map(group => (
                <div className="summary-group" key={group.title}>
                  <div className="summary-group-title">{group.title}</div>
                  <div className="summary-group-list">
                    {group.items.map(item => (
                      <div className="summary-row" key={item.label}>
                        <span className="summary-row-label">{item.label}</span>
                        <span className="summary-row-value">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
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
                isDarkMode={isDarkMode}
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
