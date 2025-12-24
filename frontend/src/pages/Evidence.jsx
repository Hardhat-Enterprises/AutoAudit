// Evidence Scanner page (frontend).
//
// This file contains:
// - The UI for selecting a strategy + uploading evidence
// - The "Scan Evidence" button click handler (calls the API)
// - Rendering the scan results table returned by the backend
//
// Backend endpoints used (see backend-api/app/api/v1/evidence.py):
// - GET  /v1/evidence/strategies  -> list strategies for dropdown
// - POST /v1/evidence/scan        -> run scan on uploaded file
// - GET  /v1/evidence/reports/:id -> download a generated report
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { getEvidenceReportUrl, getEvidenceStrategies, scanEvidence } from '../api/client';
import { useAuth } from '../context/AuthContext';
import './Evidence.css';

// If the validator finds fewer than this number of expected terms for the selected strategy,
// treat the scan as "not readable / not relevant" and suppress findings in the UI.
const MIN_VALIDATOR_MATCHED_TERMS = 2;

const EvidenceExtract = ({ evidence }) => {
  // Frontend helper to render the "Evidence Extract" cell.
  // The backend returns `finding.evidence` as an array of strings (or sometimes an object),
  // and we normalize that into display text for the <pre> block.
  const text = useMemo(() => {
    if (!evidence) return '';
    if (Array.isArray(evidence)) {
      return evidence
        .filter(Boolean)
        .map((item) => String(item).trim())
        .filter(Boolean)
        .join('\n');
    }
    if (typeof evidence === 'object') {
      try {
        return JSON.stringify(evidence, null, 2);
      } catch {
        return String(evidence);
      }
    }
    return String(evidence).trim();
  }, [evidence]);

  if (!text) return <span>—</span>;

  return (
    <div className="evidence-cell">
      <div className="evidence-block">
        {/* Styled by .evidence-block__body in Evidence.css (monospace, wrap, max-height scroll). */}
        <pre className="evidence-block__body">{text}</pre>
      </div>
    </div>
  );
};

const Evidence = ({ sidebarWidth = 220, isDarkMode = true }) => {
  // ------------------------------
  // Frontend UI state (React).
  // ------------------------------
  // Available strategies to show in the dropdown (fetched from backend).

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
      import.meta.env.VITE_EVIDENCE_API_BASE,
      import.meta.env.VITE_EVIDENCE_API,
      import.meta.env.VITE_API_URL,
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
  // Currently selected strategy name (used in scan request).
  const [selectedStrategy, setSelectedStrategy] = useState('');
  // The file chosen in the <input type="file"> (sent to backend).
  const [selectedFile, setSelectedFile] = useState(null);
  // While a scan request is in-flight (used to disable button + show spinner).
  const [isScanning, setIsScanning] = useState(false);
  // User-facing error message for strategy load / scan errors.
  const [error, setError] = useState('');
  // Full JSON payload returned by the backend scan endpoint.
  const [results, setResults] = useState(null);
  // While we're loading strategies for the dropdown.
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(true);

  // File input is uncontrolled (browser-owned), so keep a ref to clear it when we reset state.
  // This prevents the UI from showing a filename while `selectedFile` is null (which disables the scan button).
  const fileInputRef = useRef(null);

  // Auth token from AuthContext (frontend).
  // Used as Bearer token when calling POST /v1/evidence/scan.
  const { token } = useAuth();

  // If the backend returned a validator payload, use it to decide whether the scan output
  // is meaningful for the chosen strategy.
  const isLowSignalScan = useMemo(() => {
    const summary = results?.validator?.summary;
    if (!summary) return false;

    const totalTerms = Number(summary.totalTerms ?? 0);
    const matchedCount = Number(summary.matchedCount ?? 0);

    // If the strategy has no validator terms (totalTerms=0), don't suppress anything.
    if (!Number.isFinite(totalTerms) || totalTerms <= 0) return false;

    return matchedCount < MIN_VALIDATOR_MATCHED_TERMS;
  }, [results]);

  // Normalize `results.findings` into a safe array for rendering.
  const findings = useMemo(() => {
    if (!results || !Array.isArray(results.findings)) return [];
    if (isLowSignalScan) return [];
    return results.findings;
  }, [results, isLowSignalScan]);

  // Lightweight counts used for the "Results" chips (pass/fail/warn).
  const resultsSummary = useMemo(() => {
    const summary = { total: findings.length, pass: 0, fail: 0, warning: 0, other: 0 };
    for (const finding of findings) {
      const status = String(finding?.pass_fail || '').toUpperCase();
      if (status === 'PASS') summary.pass += 1;
      else if (status === 'FAIL') summary.fail += 1;
      else if (status === 'WARNING') summary.warning += 1;
      else summary.other += 1;
    }
    return summary;
  }, [findings]);

  // Reports returned by the backend (filenames in the reports output dir).
  // We de-duplicate in case the backend returns the same filename multiple times.
  const reportFiles = useMemo(() => {
    if (isLowSignalScan) return [];
    const list = results?.reports;
    if (!Array.isArray(list)) return [];
    return Array.from(new Set(list.filter(Boolean)));
  }, [results, isLowSignalScan]);

  // On page load (mount), fetch strategies so the user can pick one.
  // Frontend -> Backend: GET /v1/evidence/strategies (see api/client.js).
  useEffect(() => {
    const fetchStrategies = async () => {
      setIsLoadingStrategies(true);
      try {
        const data = await getEvidenceStrategies();
        setStrategies(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message || 'Unable to load strategies.');
      } finally {
        setIsLoadingStrategies(false);
      }
    };

    fetchStrategies();
  }, []);

  // Resolve the selected strategy object (description + evidence types) for UI hints.
  const selectedStrategyData = useMemo(
    () => strategies.find((s) => s.name === selectedStrategy),
    [strategies, selectedStrategy]
  );

  // Build the file input "accept" list (frontend-only).
  // If the backend provides evidence_types for a strategy, we use it; otherwise we allow a broad set.
  const acceptedFileTypes = useMemo(() => {
    const fallback = [
      'pdf',
      'png',
      'jpg',
      'jpeg',
      'tif',
      'tiff',
      'bmp',
      'webp',
      'txt',
      'docx',
      'csv',
      'log',
      'reg',
      'ini',
      'json',
      'xml',
      'htm',
      'html'
    ];
    const list =
      selectedStrategyData?.evidence_types && selectedStrategyData.evidence_types.length > 0
        ? selectedStrategyData.evidence_types
        : fallback;
    return list.map((ext) => (ext.startsWith('.') ? ext : `.${ext}`)).join(',');
  }, [selectedStrategyData]);

  // When the user picks a different strategy:
  // - clear the selected file (since file requirements may change)
  // - clear previous results/errors to avoid confusion
  const handleStrategyChange = (e) => {
    setSelectedStrategy(e.target.value);
    setSelectedFile(null);
    // Also clear the native file input value so the browser UI matches our state.
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setResults(null);
    setError('');
  };

  // When the user selects a file:
  // - store the File object for upload
  // - clear any previous error
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    setSelectedFile(file || null);
    setError('');
  };

  // "Scan Evidence" click handler (frontend).
  //
  // Flow:
  // 1) Validate required inputs (strategy + file)
  // 2) POST multipart/form-data to backend /v1/evidence/scan
  //    - handled by backend-api/app/api/v1/evidence.py
  //    - which delegates scanning to security/evidence_ui/app.py
  // 3) Store the JSON response in `results` to render the table below
  const handleScan = async () => {
    setError('');

    if (!selectedStrategy) {
      setError('Please select a strategy.');
      return;
    }

    if (!selectedFile) {
      setError('Please choose an evidence file.');
      return;
    }

    setIsScanning(true);

    try {
      // Frontend -> Backend call lives in api/client.js (scanEvidence()).
      const data = await scanEvidence(token, {
        strategyName: selectedStrategy,
        file: selectedFile,
      });
      // Backend returns an object like:
      // { ok: true, findings: [...], reports: [...], note?: string }
      setResults(data);
    } catch (err) {
      setError(err.message || 'Scan failed. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  // Map PASS/FAIL/WARNING to CSS badge classes (frontend).
  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'PASS':
        return 'status-pass';
      case 'FAIL':
        return 'status-fail';
      case 'WARNING':
        return 'status-warning';
      default:
        return 'status-muted';
    }
  };

  return (
    <div
      className={`evidence-scanner ${isDarkMode ? 'dark' : 'light'}`}
      style={{
        // Layout: keep page content aligned with collapsible sidebar width.
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
      }}
    >
      <div className="evidence-container">
        <div className="brand-wrap">
          <div className="brand-content">
            <img src="/AutoAudit.png" alt="AutoAudit Logo" className="brand-logo" />
            <h1 className="brand-title">Evidence Scanner</h1>
          </div>
        </div>

        <p className="evidence-subtitle">
          Your Evidence Assistant: Pick a strategy and upload your file. Images, PDF, DOCX, TXT, logs, registry exports
          are supported.
        </p>

        <div className="evidence-card">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="strategy" className="form-label">
                Strategy
              </label>
              <select
                id="strategy"
                className="form-select"
                value={selectedStrategy}
                // Disable dropdown while loading strategy list from backend.
                disabled={isLoadingStrategies}
                onChange={handleStrategyChange}
              >
                <option value="">{isLoadingStrategies ? 'Loading strategies…' : '— select a strategy —'}</option>
                {strategies.map((strategy) => (
                  <option key={strategy.name} value={strategy.name}>
                    {strategy.name}
                  </option>
                ))}
              </select>
              {selectedStrategyData && (
                <div className="form-help">
                  {selectedStrategyData.description}
                  <br />
                  <strong>Category:</strong> {selectedStrategyData.category} · <strong>Severity:</strong>{' '}
                  {selectedStrategyData.severity}
                  <br />
                  <strong>Evidence types:</strong> {selectedStrategyData.evidence_types?.join(', ')}
                </div>
              )}
            </div>
          </div>

          <div className="file-group">
            <label htmlFor="file" className="form-label">
              Evidence file
            </label>
            <input
              id="file"
              type="file"
              className="form-file"
              ref={fileInputRef}
              // Require a strategy first (so we can set accept list + UX guidance).
              disabled={!selectedStrategy}
              accept={acceptedFileTypes}
              onChange={handleFileChange}
            />
            <div className="file-name">{selectedFile ? selectedFile.name : 'Choose an evidence file.'}</div>
            <div className="file-help">Enabled after you choose a strategy.</div>
          </div>

          <div className="actions">
            <button
              className="btn btn-primary"
              // Disable until strategy + file selected (and while scanning).
              disabled={!selectedStrategy || !selectedFile || isScanning}
              onClick={handleScan}
            >
              {isScanning ? (
                <>
                  <span className="spinner" />
                  Scanning...
                </>
              ) : (
                'Scan Evidence'
              )}
            </button>

            {error && <span className="status-error">{error}</span>}
          </div>
        </div>

        {results && (
          <div className="results-card">
            <div className="results-title-row">
              <h3 className="results-header">Results</h3>
              <div className="results-kpis">
                {/* Prefer a single download action instead of repeating a link per row. */}
                {reportFiles.length > 0 && (
                  <a
                    href={getEvidenceReportUrl(reportFiles[0])}
                    className="report-link"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download PDF
                  </a>
                )}
                <span className="kpi-chip kpi-total">{resultsSummary.total} total</span>
                <span className="kpi-chip kpi-pass">{resultsSummary.pass} pass</span>
                <span className="kpi-chip kpi-fail">{resultsSummary.fail} fail</span>
                <span className="kpi-chip kpi-warn">{resultsSummary.warning} warn</span>
              </div>
            </div>

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

            {results.note && (
              <div className="note-banner" role="status">
                {/* Backend-supplied note (e.g. "No readable text found"). */}
                {results.note}
              </div>
            )}

            {findings.length > 0 ? (
              <div className="results-table-wrap">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Test ID</th>
                      <th>Sub-Strategy</th>
                      <th>Status</th>
                      <th>Recommendation</th>
                      <th>Evidence Extract</th>
                    </tr>
                  </thead>
                  <tbody>
                    {findings.map((finding, index) => {
                      return (
                        <tr className="results-row" key={index}>
                          <td>
                            <span className="mono">{finding.test_id || '—'}</span>
                          </td>
                          <td>{finding.sub_strategy}</td>
                          <td>
                            <span className={`result-badge ${getStatusClass(finding.pass_fail)}`}>
                              {finding.pass_fail || '—'}
                            </span>
                          </td>
                          <td>
                            <div className="cell-clamp" title={finding.recommendation || ''}>
                              {finding.recommendation || '—'}
                            </div>
                          </td>
                          <td>
                            <EvidenceExtract evidence={finding.evidence} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-findings">
                {isLowSignalScan
                  ? 'No readable text found (or the file does not match the selected strategy).'
                  : 'No readable text found or no findings.'}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Evidence;
