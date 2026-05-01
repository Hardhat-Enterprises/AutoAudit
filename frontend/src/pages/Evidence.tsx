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

// If the validator finds fewer than this number of expected terms for the selected strategy,
// treat the scan as "not readable / not relevant" and suppress findings in the UI.
const MIN_VALIDATOR_MATCHED_TERMS = 1;

// Types for backend payloads
type EvidenceStrategy = {
  name: string;
  description?: string;
  category?: string;
  severity?: string;
  evidence_types?: string[];
};
type EvidenceFinding = {
  test_id?: string;
  sub_strategy?: string;
  pass_fail?: string;
  recommendation?: string;
  evidence?: unknown;
};
type ValidatorSummary = { totalTerms?: number; matchedCount?: number };
type EvidenceResults = {
  validator?: { summary?: ValidatorSummary };
  findings?: EvidenceFinding[];
  reports?: string[];
  note?: string;
};
type EvidencePageProps = { sidebarWidth?: number; isDarkMode?: boolean };

const EvidenceExtract = ({ evidence }: { evidence: unknown }) => {
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
    <div className="flex flex-col gap-1.5">
      <div className="border-0 p-0 bg-transparent">
        <pre className="m-0 whitespace-pre-wrap text-[13px] leading-snug wrap-break-word px-3 py-2.5 border border-border-subtle rounded-xl bg-surface-1 max-h-40 overflow-auto" style={{ fontFamily: '"SFMono-Regular", "Menlo", "Consolas", monospace' }}>{text}</pre>
      </div>
    </div>
  );
};

const Evidence = ({ sidebarWidth = 220, isDarkMode = true }: EvidencePageProps) => {
  // ------------------------------
  // Frontend UI state (React).
  // ------------------------------
  // Available strategies to show in the dropdown (fetched from backend).

  const [observedSidebarWidth, setObservedSidebarWidth] = useState<number>(sidebarWidth);

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
      .filter((r): r is string => typeof r === 'string' && r.length > 0)
      .map((root) => root.replace(/\/+$/, ''));

    const urls = roots.map((root) => `${root}/v1/evidence`);

    return urls.filter((url, idx) => urls.indexOf(url) === idx);
  }, []);

  const [apiBase, setApiBase] = useState<string>(() => apiCandidates[0] || '');
  const [strategies, setStrategies] = useState<EvidenceStrategy[]>([]);
  // Currently selected strategy name (used in scan request).
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  // The file chosen in the <input type="file"> (sent to backend).
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  // While a scan request is in-flight (used to disable button + show spinner).
  const [isScanning, setIsScanning] = useState(false);
  // User-facing error message for strategy load / scan errors.
  const [error, setError] = useState<string>('');
  // Full JSON payload returned by the backend scan endpoint.
  const [results, setResults] = useState<EvidenceResults | null>(null);
  // While we're loading strategies for the dropdown.
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(true);

  // File input is uncontrolled (browser-owned), so keep a ref to clear it when we reset state.
  // This prevents the UI from showing a filename while `selectedFile` is null (which disables the scan button).
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Auth token from AuthContext (frontend).
  // Used as Bearer token when calling POST /v1/evidence/scan.
  const { token } = useAuth();

  // If the backend returned a validator payload, use it to decide whether the scan output
  // is meaningful for the chosen strategy.
  const isLowSignalScan = useMemo(() => {
    const summary = results?.validator?.summary;
    if (!summary) {
      return false;
    }
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
        setStrategies(Array.isArray(data) ? (data as EvidenceStrategy[]) : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load strategies.');
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
    const list: string[] =
      selectedStrategyData?.evidence_types && selectedStrategyData.evidence_types.length > 0
        ? selectedStrategyData.evidence_types
        : fallback;
    return list.map((ext: string) => (ext.startsWith('.') ? ext : `.${ext}`)).join(',');
  }, [selectedStrategyData]);

  // When the user picks a different strategy:
  // - clear the selected file (since file requirements may change)
  // - clear previous results/errors to avoid confusion
  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
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
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
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
      setError(err instanceof Error ? err.message : 'Scan failed. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  // Map PASS/FAIL/WARNING to Tailwind badge classes (frontend).
  // IMPORTANT: Returns full Tailwind class strings, not CSS class names.
  // Tailwind needs to see the complete class string at build time, so we cannot
  // construct classes dynamically (e.g. `bg-${color}-500`).
  const getStatusClass = (status: unknown) => {
    const s = typeof status === 'string' ? status.toUpperCase() : String(status ?? '').toUpperCase();
    switch (s) {
      case 'PASS':
        return 'bg-accent-good/10 border-accent-good/25 text-accent-good';
      case 'FAIL':
        return 'bg-accent-bad/10 border-accent-bad/25 text-accent-bad';
      case 'WARNING':
        return 'bg-accent-warn/10 border-accent-warn/25 text-accent-warn';
      default:
        return 'bg-text-muted/10 border-text-muted/20 text-text-muted';
    }
  };

  return (
    <div
      className={`${isDarkMode ? 'dark' : 'light'} min-h-screen p-6 bg-surface-1 text-text-strong transition-colors duration-200 in-[.light]:bg-surface-1`}
      style={{
        // Layout: keep page content aligned with collapsible sidebar width.
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
      }}
    >
      <div className="w-full max-w-300 mx-auto">
        <div className="flex items-center gap-5 mb-1.5 justify-start pl-6">
          <div className="flex items-center gap-5">
            <img src="/AutoAudit.png" alt="AutoAudit Logo" className="w-40 h-40 object-contain" />
            <h1
              className="m-0 leading-none font-bold tracking-wide text-accent-teal in-[.light]:text-brand-blue"
              style={{
                fontFamily: '"League Spartan", system-ui, sans-serif',
                fontSize: 'clamp(28px, 7vw, 56px)',
              }}
            >
              Evidence Scanner
            </h1>
          </div>
        </div>

        <p className="text-text-muted mt-1.5 mb-6 ml-6 text-[15px] leading-snug text-left">
          Your Evidence Assistant: Pick a strategy and upload your file. Images, PDF, DOCX, TXT, logs, registry exports
          are supported.
        </p>

        <div className="border border-border-subtle rounded-2xl p-6 bg-surface-2 shadow-[0_4px_12px_rgba(0,0,0,0.1)] mb-6 transition-all duration-300">
          <div className="grid grid-cols-1 gap-5 mb-5">
            <div className="flex flex-col">
              <label htmlFor="strategy" className="block mb-2 font-semibold text-text-strong text-sm">
                Strategy
              </label>
              <select
                id="strategy"
                className="w-full px-3.5 py-3 border border-border-subtle rounded-[10px] text-[15px] bg-surface-1 text-text-strong transition-all duration-300 appearance-none pr-10 min-h-11.5 leading-snug bg-no-repeat focus:outline-none focus:border-accent-teal focus:ring-2 focus:ring-accent-teal/20 disabled:opacity-60 disabled:cursor-not-allowed in-[.light]:bg-surface-2 in-[.light]:text-text-strong"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%2394a3b8' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
                  backgroundPosition: 'right 12px center',
                  backgroundSize: '12px 8px',
                }}
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
                <div className="text-text-muted text-[13px] mt-1.5 leading-snug">
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

          <div className="mt-5">
            <label htmlFor="file" className="block mb-2 font-semibold text-text-strong text-sm">
              Evidence file
            </label>
            <input
              id="file"
              type="file"
              className="w-full cursor-pointer px-3.5 py-3 border border-border-subtle rounded-[10px] text-[15px] bg-surface-1 text-text-strong transition-all duration-300 focus:outline-none focus:border-accent-teal focus:ring-2 focus:ring-accent-teal/20 disabled:opacity-60 disabled:cursor-not-allowed in-[.light]:bg-surface-2 in-[.light]:text-text-strong"
              ref={fileInputRef}
              // Require a strategy first (so we can set accept list + UX guidance).
              disabled={!selectedStrategy}
              accept={acceptedFileTypes}
              onChange={handleFileChange}
            />
            <div className="text-text-muted text-[13px] mt-1.5">
              {selectedFile ? selectedFile.name : 'Choose an evidence file.'}
            </div>
            <div className="text-text-muted text-xs mt-1 opacity-70">
              Enabled after you choose a strategy.
            </div>
          </div>

          <div className="mt-6 flex items-center gap-3 flex-wrap">
            <button
              className="px-5 py-3 border rounded-[10px] cursor-pointer font-semibold text-[15px] transition-all duration-300 flex items-center gap-2 bg-accent-teal text-accent-navy border-accent-teal hover:bg-brand-cyan hover:border-brand-cyan hover:shadow-[0_4px_12px_rgb(var(--brand-cyan))] disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:bg-brand-cyan disabled:hover:border-brand-cyan"
              // Disable until strategy + file selected (and while scanning).
              disabled={!selectedStrategy || !selectedFile || isScanning}
              onClick={handleScan}
            >
              {isScanning ? (
                <>
                  <span className="w-4 h-4 border-2 border-text-muted border-t-accent-teal rounded-full animate-spin" />
                  Scanning...
                </>
              ) : (
                'Scan Evidence'
              )}
            </button>

            {error && <span className="text-accent-bad font-semibold text-sm">{error}</span>}
          </div>
        </div>

        {results && (
          <div className="border border-border-subtle rounded-2xl p-6 bg-surface-2 shadow-[0_4px_12px_rgba(0,0,0,0.1)] transition-all duration-300 w-full overflow-hidden">
            <div className="flex items-start justify-between gap-4 flex-wrap mb-4">
              <h3 className="m-0 text-text-strong text-xl font-semibold">Results</h3>
              <div className="flex items-center gap-2 flex-wrap">
                {/* Prefer a single download action instead of repeating a link per row. */}
                {reportFiles.length > 0 && (
                  <a
                    href={getEvidenceReportUrl(reportFiles[0])}
                    className="inline-flex items-center justify-center px-2.5 py-1.5 rounded-full border border-accent-teal/35 bg-accent-teal/8 text-accent-teal no-underline font-bold text-xs leading-none hover:text-brand-cyan hover:bg-accent-teal/14 hover:border-accent-teal/60 focus-visible:outline focus-visible:outline-accent-teal/70 focus-visible:outline-offset-2"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download PDF
                  </a>
                )}
                <span className="inline-flex items-center justify-center px-2.5 py-1.5 rounded-full border border-border-subtle bg-border-subtle text-text-strong text-xs font-semibold leading-none whitespace-nowrap">
                  {resultsSummary.total} total
                </span>
                <span className="inline-flex items-center justify-center px-2.5 py-1.5 rounded-full border border-accent-good/25 bg-accent-good/10 text-accent-good text-xs font-semibold leading-none whitespace-nowrap">
                  {resultsSummary.pass} pass
                </span>
                <span className="inline-flex items-center justify-center px-2.5 py-1.5 rounded-full border border-accent-bad/25 bg-accent-bad/10 text-accent-bad text-xs font-semibold leading-none whitespace-nowrap">
                  {resultsSummary.fail} fail
                </span>
                <span className="inline-flex items-center justify-center px-2.5 py-1.5 rounded-full border border-accent-warn/25 bg-accent-warn/10 text-accent-warn text-xs font-semibold leading-none whitespace-nowrap">
                  {resultsSummary.warning} warn
                </span>
              </div>
            </div>

            <div className="mb-3 flex gap-4 flex-wrap">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 border border-border-subtle rounded-full text-xs text-text-muted bg-border-subtle min-w-0">
                <span className="text-text-muted text-[11px] font-bold tracking-wider uppercase whitespace-nowrap">Strategy</span>
                <span className="text-text-strong font-semibold overflow-hidden text-ellipsis whitespace-nowrap max-w-105">{selectedStrategy}</span>
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 border border-border-subtle rounded-full text-xs text-text-muted bg-border-subtle min-w-0">
                <span className="text-text-muted text-[11px] font-bold tracking-wider uppercase whitespace-nowrap">File</span>
                <span className="text-text-strong font-semibold overflow-hidden text-ellipsis whitespace-nowrap max-w-105">{selectedFile?.name}</span>
              </div>
            </div>

            {results.note && (
              <div className="border border-border-subtle border-l-4 border-l-accent-teal bg-surface-2 text-text-strong px-3.5 py-3 rounded-[10px] mb-5 leading-snug" role="status">
                {/* Backend-supplied note (e.g. "No readable text found"). */}
                {results.note}
              </div>
            )}

            {findings.length > 0 ? (
              <div className="mt-4 border border-border-subtle rounded-xl overflow-x-auto overflow-y-visible bg-surface-2">
                <table className="w-full border-collapse text-sm min-w-7xl">
                  <thead>
                    <tr>
                      <th className="px-4 py-3.5 text-left align-top bg-border-subtle text-text-muted font-bold text-xs uppercase tracking-wider border-b border-border-subtle whitespace-nowrap">Test ID</th>
                      <th className="px-4 py-3.5 text-left align-top bg-border-subtle text-text-muted font-bold text-xs uppercase tracking-wider border-b border-border-subtle whitespace-nowrap">Sub-Strategy</th>
                      <th className="px-4 py-3.5 text-left align-top bg-border-subtle text-text-muted font-bold text-xs uppercase tracking-wider border-b border-border-subtle whitespace-nowrap">Status</th>
                      <th className="px-4 py-3.5 text-left align-top bg-border-subtle text-text-muted font-bold text-xs uppercase tracking-wider border-b border-border-subtle whitespace-nowrap min-w-[320px] max-w-130">Recommendation</th>
                      <th className="px-4 py-3.5 text-left align-top bg-border-subtle text-text-muted font-bold text-xs uppercase tracking-wider border-b border-border-subtle whitespace-nowrap min-w-130">Evidence Extract</th>
                    </tr>
                  </thead>
                  <tbody>
                    {findings.map((finding: EvidenceFinding, index: number) => {
                      const isLast = index === findings.length - 1;
                      const borderClass = isLast ? '' : 'border-b border-border-subtle';
                      return (
                        <tr className="group" key={index}>
                          <td className={`px-4 py-3.5 text-left align-top bg-surface-2 text-text-strong ${borderClass} group-hover:bg-border-subtle`}>
                            <span className="inline-flex items-center px-2 py-0.5 rounded-lg border border-border-subtle bg-surface-1 text-xs text-text-muted whitespace-nowrap" style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace' }}>
                              {finding.test_id || '—'}
                            </span>
                          </td>
                          <td className={`px-4 py-3.5 text-left align-top bg-surface-2 text-text-strong ${borderClass} group-hover:bg-border-subtle`}>
                            {finding.sub_strategy}
                          </td>
                          <td className={`px-4 py-3.5 text-left align-top bg-surface-2 text-text-strong ${borderClass} group-hover:bg-border-subtle`}>
                            <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full border text-xs font-bold leading-none whitespace-nowrap ${getStatusClass(finding.pass_fail)}`}>
                              {finding.pass_fail || '—'}
                            </span>
                          </td>
                          <td className={`px-4 py-3.5 text-left align-top bg-surface-2 text-text-strong ${borderClass} group-hover:bg-border-subtle min-w-[320px] max-w-130 wrap-break-word`}>
                            <div className="line-clamp-3 leading-snug wrap-break-word" title={finding.recommendation || ''}>
                              {finding.recommendation || '—'}
                            </div>
                          </td>
                          <td className={`px-4 py-3.5 text-left align-top bg-surface-2 text-text-strong ${borderClass} group-hover:bg-border-subtle min-w-130`}>
                            <EvidenceExtract evidence={finding.evidence} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-text-muted italic text-center py-10 px-5">
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
