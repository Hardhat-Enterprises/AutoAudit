import React, { useState, useEffect, useMemo } from 'react';
import './Evidence.css';
import { useNavigate } from 'react-router-dom';
import { parseApiError, formatEvidenceList } from '../utils/api';

const EvidenceDetails = ({ details, evidence }) => {
  const toText = (value) => {
    if (!value) return '';
    if (Array.isArray(value)) {
      return value
        .filter(Boolean)
        .map((item) => String(item).trim())
        .join('\n');
    }
    if (typeof value === 'object') {
      const stringifiable = value.observed || value.expected || value.recommendation;
      if (!stringifiable) return '';
      return String(stringifiable).trim();
    }
    return String(value).trim();
  };

  const observed = toText(
    details?.observed_full ??
    details?.observed ??
    (Array.isArray(details?.evidence) ? details.evidence : details?.evidence)
  );

  const evidenceList = formatEvidenceList(evidence);
  const merged = [observed, evidenceList.join('\n')].filter(Boolean).join('\n').trim();
  const hasContent = merged.length > 0;

  if (!hasContent) return <span>—</span>;

  return (
    <div className="evidence-cell">
      <div className="evidence-block">
        <pre className="evidence-block__body">
          {merged}
        </pre>
      </div>
    </div>
  );
};

const Evidence = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const [observedSidebarWidth, setObservedSidebarWidth] = useState(sidebarWidth);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof ResizeObserver === 'undefined') {
      setObservedSidebarWidth(sidebarWidth);
      return;
    }
    const sidebarEl = document.querySelector('.sidebar');
    if (!sidebarEl) {
      setObservedSidebarWidth(sidebarWidth);
      return;
    }
    const observer = new ResizeObserver((entries) => {
      const width = entries?.[0]?.contentRect?.width;
      if (width && Math.abs(width - observedSidebarWidth) > 1) {
        setObservedSidebarWidth(width);
      }
    });
    observer.observe(sidebarEl);
    return () => observer.disconnect();
  }, [sidebarWidth, observedSidebarWidth]);

  const apiCandidates = useMemo(() => {
    const roots = [
      process.env.REACT_APP_EVIDENCE_API_BASE,
      process.env.REACT_APP_EVIDENCE_API,
      process.env.REACT_APP_API_URL,
      typeof window !== 'undefined' ? window.location.origin : null,
      'http://localhost:8000',
    ]
      .filter(Boolean)
      .map((root) => root.replace(/\/+$/, ''));

    const urls = roots.map((root) => `${root}/v1/evidence`);

    return urls.filter((url, idx) => urls.indexOf(url) === idx);
  }, []);

  const [apiBase, setApiBase] = useState(() => apiCandidates[0] || '');
  const [strategies, setStrategies] = useState([]);
  const [strategiesLoading, setStrategiesLoading] = useState(false);
  const [strategiesError, setStrategiesError] = useState('');
  const [health, setHealth] = useState(null);

  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [userId, setUserId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  const [errorDetails, setErrorDetails] = useState([]);
  const [note, setNote] = useState('');
  const [results, setResults] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    let isActive = true;

    const fetchStrategies = async () => {
      setStrategiesLoading(true);
      setStrategiesError('');

      for (const base of apiCandidates) {
        try {
          const res = await fetch(`${base}/strategies`);
          if (!res.ok) {
            const parsed = await parseApiError(res, `Failed to load strategies (${res.status})`);
            throw new Error(parsed.message);
          }
          const data = await res.json();
          if (!isActive) {
            return;
          }

          setStrategies(Array.isArray(data) ? data : []);
          setApiBase(base);
          setStrategiesLoading(false);
          return;
        } catch (err) {
          // try the next candidate
        }
      }

      if (isActive) {
        setStrategiesError('Unable to load strategies from the Evidence API.');
        setStrategies([]);
        setApiBase(apiCandidates[0] || '');
        setStrategiesLoading(false);
      }
    };

    fetchStrategies();
    return () => { isActive = false; };
  }, [apiCandidates]);

  useEffect(() => {
    if (!apiBase) {
      return;
    }
    let isActive = true;

    const fetchHealth = async () => {
      try {
        const res = await fetch(`${apiBase}/health`);
        if (!res.ok) return;
        const data = await res.json();
        if (isActive) setHealth(data);
      } catch (err) {
        // health is best-effort
      }
    };

    fetchHealth();
    return () => { isActive = false; };
  }, [apiBase]);

  const handleStrategyChange = (e) => {
    setSelectedStrategy(e.target.value);
    setError('');
    setErrorDetails([]);
    setResults(null);
    setNote('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    setSelectedFile(file || null);
    setError('');
    setErrorDetails([]);
  };

  const handleScan = async () => {
    setError('');
    setErrorDetails([]);
    setNote('');
    const base = apiBase || apiCandidates[0];

    if (!base) {
      setError('Evidence API is not configured.');
      return;
    }

    if (!selectedStrategy) {
      setError('Please select a strategy.');
      return;
    }

    if (!selectedFile) {
      setError('Please choose an evidence file.');
      return;
    }

    setIsScanning(true);

    const formData = new FormData();
    // Send strategy under both names to satisfy legacy and current API handlers
    formData.append('strategy_name', selectedStrategy);
    formData.append('strategy', selectedStrategy);
    formData.append('user_id', userId || 'user');
    formData.append('evidence', selectedFile);

    try {
      const res = await fetch(`${base}/scan`, {
        method: 'POST',
        body: formData
      });

      const raw = await res.text();
      let data = {};
      try {
        data = JSON.parse(raw);
      } catch (err) {
        throw new Error(raw?.slice(0, 160) || 'Scan failed.');
      }

      if (!res.ok || data.ok === false) {
        const errs = Array.isArray(data?.errors) ? data.errors : [];
        const errMsg =
          errs[0]?.message ||
          data?.detail ||
          `Scan failed (${res.status})`;
        setErrorDetails(errs);
        throw new Error(errMsg);
      }

      setResults(data);
      setNote(data?.note || '');
      setErrorDetails(Array.isArray(data?.errors) ? data.errors : []);
    } catch (err) {
      setError(err?.message || 'Scan failed. Please try again.');
      setResults(null);
    } finally {
      setIsScanning(false);
    }
  };

  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'PASS': return 'status-pass';
      case 'FAIL': return 'status-fail';
      case 'WARNING': return 'status-warning';
      default: return '';
    }
  };

  const selectedStrategyData = useMemo(
    () => strategies.find((s) => s.name === selectedStrategy),
    [strategies, selectedStrategy]
  );

  const openRecentScans = () => {
    const base = apiBase || apiCandidates[0];
    if (base) {
      window.open(`${base}/scan-mem`, '_blank', 'noopener');
    }
  };

  const buildReportLink = (filename) => {
    const base = apiBase || apiCandidates[0] || '';
    return base ? `${base}/reports/${encodeURIComponent(filename)}` : '#';
  };

  return (
    <div 
      className={`evidence-scanner ${isDarkMode ? 'dark' : 'light'}`}
      style={{ 
        marginLeft: `${observedSidebarWidth}px`, 
        width: `calc(100vw - ${observedSidebarWidth}px)`,
        transition: 'none'
      }}
    >
      <div className="evidence-container">
        {/* Back Button - Fixed to go to Dashboard */}
        <div className="nav-breadcrumb">
          <span className="nav-link" onClick={() => navigate("/dashboard")}>
            ← Back
          </span>
        </div>

        {/* Brand Header */}
        <div className="brand-wrap">
          <div className="brand-content">
            <img 
              src="/AutoAudit.png" 
              alt="AutoAudit Logo" 
              className="brand-logo"
            />
            <h1 className="brand-title">Evidence Scanner</h1>
          </div>
        </div>

        <p className="evidence-subtitle">
          Your Evidence Assistant: Pick a strategy and upload your file. Images, PDF, DOCX, TXT, logs, registry exports are supported.
        </p>

        <div className="pill-row">
          {strategiesLoading && <span className="status-busy">Loading strategies…</span>}
          {strategiesError && <span className="status-error">{strategiesError}</span>}
        </div>

        {/* Main Form Card */}
        <div className="evidence-card">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="strategy" className="form-label">Strategy</label>
              <select 
                id="strategy" 
                className="form-select"
                value={selectedStrategy}
                onChange={handleStrategyChange}
                disabled={strategiesLoading || !strategies.length}
              >
                <option value="">{strategiesLoading ? 'Loading…' : '— select a strategy —'}</option>
                {strategies.map((strategy) => (
                  <option key={strategy.name} value={strategy.name}>
                    {strategy.name}
                  </option>
                ))}
              </select>
              {selectedStrategyData && (
                <div className="form-help">{selectedStrategyData.description}</div>
              )}
              {!strategiesLoading && !strategies.length && !strategiesError && (
                <div className="form-help">No strategies returned by the API.</div>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="user" className="form-label">User ID (optional)</label>
              <input 
                id="user" 
                type="text" 
                className="form-input"
                placeholder="e.g. bharadwaj"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
            </div>
          </div>

          <div className="file-group">
            <label htmlFor="file" className="form-label">Evidence file</label>
            <input 
              id="file" 
              type="file" 
              className="form-file"
              disabled={!selectedStrategy || strategiesLoading}
              accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp,.txt,.docx,.csv,.log,.reg,.ini,.json,.xml,.htm,.html"
              onChange={handleFileChange}
            />
            <div className="file-name">
              {selectedFile ? selectedFile.name : 'Choose an evidence file.'}
            </div>
            <div className="file-help">
              Enabled after you choose a strategy.
            </div>
          </div>

          <div className="actions">
            <button 
              className="btn btn-primary" 
              disabled={!selectedStrategy || !selectedFile || isScanning}
              onClick={handleScan}
            >
              {isScanning ? (
                <>
                  <span className="spinner"></span>
                  Scanning...
                </>
              ) : (
                'Scan Evidence'
              )}
            </button>

            <button 
              className="btn btn-secondary"
              type="button"
              onClick={openRecentScans}
            >
              Recent Scans
            </button>

            {error && <span className="status-error">{error}</span>}
            {errorDetails.length > 0 && (
              <ul className="error-list">
                {errorDetails.map((err, idx) => (
                  <li key={idx}>
                    {err.code ? `[${err.code}] ` : ''}{err.message || JSON.stringify(err)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {note && (
          <div className="note-banner" role="status">{note}</div>
        )}

        {/* Results Section */}
        {results && (
          <div className="results-card">
            <h3 className="results-header">Results</h3>
            
            <div className="results-meta">
              <div className="meta-tag">
                <span>Strategy</span>
                <span>{selectedStrategy}</span>
              </div>
              <div className="meta-tag">
                <span>File</span>
                <span>{selectedFile?.name}</span>
              </div>
            </div>

            {results.findings && results.findings.length > 0 ? (
              <table className="results-table">
                <thead>
                  <tr>
                    <th>Test ID</th>
                    <th>Sub-Strategy</th>
                    <th>Level</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Recommendation</th>
                    <th>Evidence / Evidence Extract</th>
                    <th>Report</th>
                  </tr>
                </thead>
                <tbody>
                  {results.findings.map((finding, index) => (
                    <tr key={index}>
                      <td>{finding.test_id}</td>
                      <td>{finding.sub_strategy}</td>
                      <td>{finding.detected_level}</td>
                      <td className={getStatusClass(finding.pass_fail)}>
                        {finding.pass_fail}
                      </td>
                      <td>{finding.priority}</td>
                      <td>{finding.recommendation}</td>
                      <td>
                        <EvidenceDetails 
                          details={finding.details} 
                          evidence={finding.evidence} 
                        />
                      </td>
                      <td>
                        {results.reports?.[index] && (
                          <a 
                            href={buildReportLink(results.reports[index])} 
                            className="evidence-link"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            PDF
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="no-findings">
                No readable text found or no findings.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Evidence;
