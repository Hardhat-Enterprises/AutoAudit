import React, { useState, useEffect, useCallback, JSX } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getScan } from '../api/client';
import { RelativeTime } from './RelativeTime';

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
  if ((err as { message?: string })?.message) return (err as { message: string }).message;
  return fallback;
}

function compareControlIdAscending(a: ScanResult, b: ScanResult): number {
  const aId = (a?.control_id ?? '').toString();
  const bId = (b?.control_id ?? '').toString();
  const aParts = aId.split('.').map((s) => Number.parseInt(s, 10));
  const bParts = bId.split('.').map((s) => Number.parseInt(s, 10));

  const len = Math.max(aParts.length, bParts.length);
  for (let i = 0; i < len; i++) {
    const av = Number.isFinite(aParts[i]) ? aParts[i] : -1;
    const bv = Number.isFinite(bParts[i]) ? bParts[i] : -1;
    if (av !== bv) return av - bv;
  }
  return aId.localeCompare(bId);
}

const ScanDetailPage: React.FC<ScanDetailPageProps> = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadScan = useCallback(async (): Promise<ScanDetail | null> => {
    if (!scanId) {
      setError('Scan ID is missing');
      return null;
    }

    try {
      const scanData = await getScan(token, scanId);
      setScan(scanData as ScanDetail);
      setError(null);
      return scanData as ScanDetail;
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load scan'));
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
    if (!scan || scan.status === 'completed' || scan.status === 'failed') return;

    const interval = setInterval(async () => {
      const updatedScan = await loadScan();
      if (updatedScan?.status === 'completed' || updatedScan?.status === 'failed') {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [scan, loadScan]);

  function getStatusIcon(status?: string): JSX.Element {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} className="text-emerald-500" />;
      case 'failed':
        return <XCircle size={20} className="text-rose-500" />;
      case 'running':
        return <Loader2 size={20} className="text-blue-500 animate-spin" />;
      default:
        return <Clock size={20} className="text-amber-500" />;
    }
  }

  function getStatusText(status?: string): string {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'running':
        return 'Running';
      default:
        return 'Pending';
    }
  }

  function getStatusBadgeClass(status?: string): string {
    switch (status) {
      case 'completed':
        return 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/30';
      case 'failed':
        return 'bg-rose-500/15 text-rose-500 border border-rose-500/30';
      case 'running':
        return 'bg-blue-500/15 text-blue-500 border border-blue-500/30';
      default:
        return 'bg-amber-500/15 text-amber-500 border border-amber-500/30';
    }
  }

  function getResultIcon(status?: string): JSX.Element {
    switch (status) {
      case 'passed':
        return <CheckCircle size={16} className="text-emerald-500" />;
      case 'failed':
        return <XCircle size={16} className="text-rose-500" />;
      case 'error':
        return <AlertTriangle size={16} className="text-amber-500" />;
      case 'pending':
        return <Clock size={16} className="text-blue-500" />;
      default:
        return <AlertCircle size={16} className="text-slate-400" />;
    }
  }

  function getResultBadgeText(status?: string): string {
    switch (status) {
      case 'passed':
        return 'Pass';
      case 'failed':
        return 'Fail';
      case 'error':
        return 'Error';
      case 'pending':
        return 'Pending';
      case 'skipped':
        return 'Skipped';
      default:
        return 'Unknown';
    }
  }

  function getResultBadgeClass(status?: string): string {
    switch (status) {
      case 'passed':
        return 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/30';
      case 'failed':
        return 'bg-rose-500/15 text-rose-500 border border-rose-500/30';
      case 'error':
        return 'bg-amber-500/15 text-amber-500 border border-amber-500/30';
      case 'pending':
        return 'bg-blue-500/15 text-blue-500 border border-blue-500/30';
      case 'skipped':
        return 'bg-slate-500/15 text-slate-500 border border-slate-500/30';
      default:
        return 'bg-slate-500/15 text-slate-500 border border-slate-500/30';
    }
  }

  function getResultCardClass(status?: string): string {
    switch (status) {
      case 'passed':
        return 'border-emerald-500/30';
      case 'failed':
        return 'border-rose-500/30';
      case 'error':
        return 'border-amber-500/30';
      case 'pending':
        return 'border-blue-500/30';
      default:
        return 'border-slate-300 dark:border-slate-700';
    }
  }

  const pageClass = isDarkMode
    ? 'bg-slate-900 text-slate-100 transition-colors duration-300'
    : 'bg-slate-50 text-slate-900 transition-colors duration-300';

  const cardClass = isDarkMode
    ? 'rounded-xl border border-slate-700 bg-slate-800'
    : 'rounded-xl border border-slate-200 bg-white';

  const mutedText = isDarkMode ? 'text-slate-400' : 'text-slate-500';
  const subtleText = isDarkMode ? 'text-slate-300' : 'text-slate-600';

  if (isLoading) {
    return (
      <div
        className={pageClass}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
        }}
      >
        <div className="mx-auto max-w-5xl">
          <div className={`${cardClass} flex flex-col items-center justify-center p-16`}>
            <Loader2 size={32} className="text-blue-500 animate-spin" />
            <p className={`mt-4 ${subtleText}`}>Loading scan details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div
        className={pageClass}
        style={{
          width: `calc(100% - ${sidebarWidth}px)`,
        }}
      >
        <div className="mx-auto max-w-5xl">
          <div className={`${cardClass} flex flex-col items-center justify-center p-16 text-center`}>
            <AlertCircle size={48} className="text-rose-500" />
            <h3 className="mt-3 text-xl font-semibold">Failed to load scan</h3>
            <p className={`mt-2 ${subtleText}`}>{error || 'Scan not found'}</p>
            <button
              className={`mt-6 inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium ${
                isDarkMode
                  ? 'border-slate-600 bg-slate-700 text-slate-100 hover:bg-slate-600'
                  : 'border-slate-300 bg-white text-slate-800 hover:bg-slate-100'
              }`}
              onClick={() => navigate('/scans')}
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
    pending: Math.max(
      0,
      (scan.total_controls || 0) -
        (scan.passed_count || 0) -
        (scan.failed_count || 0) -
        (scan.error_count || 0) -
        (scan.skipped_count || 0),
    ),
  };

  const done = summary.passed + summary.failed + summary.errors + (scan.skipped_count || 0);

  const progressPercent =
    summary.total > 0 ? Math.min(100, Math.round((done / summary.total) * 100)) : scan.status === 'completed' ? 100 : 0;

  const results = (scan.results || [])
    .filter((r) => (r?.status || '').toLowerCase() !== 'skipped')
    .slice()
    .sort(compareControlIdAscending);

  return (
    <div
      className={pageClass}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease',
      }}
    >
      <div className="mx-auto space-y-6 max-w-5xl">
        <div className="flex justify-between items-center">
          <button
            className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium ${
              isDarkMode
                ? 'border-slate-600 bg-slate-800 text-slate-100 hover:bg-slate-700'
                : 'border-slate-300 bg-white text-slate-800 hover:bg-slate-100'
            }`}
            onClick={() => navigate('/scans')}
          >
            <ArrowLeft size={20} />
            <span>Back to Scans</span>
          </button>
        </div>

        <div className={`${cardClass} p-6`}>
          <div className="flex flex-wrap gap-4 justify-between items-start">
            <div className="flex gap-4 items-center">
              <div
                className={`rounded-xl p-3 ${
                  isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-100 text-blue-600'
                }`}
              >
                <Shield size={32} />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{scan.benchmark || 'Compliance Scan'}</h1>
                <p className={`${mutedText}`}>{scan.version || ''}</p>
              </div>
            </div>

            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${getStatusBadgeClass(scan.status)}`}>
              {getStatusIcon(scan.status)}
              {getStatusText(scan.status)}
            </span>
          </div>

          <div className="grid gap-4 mt-6 md:grid-cols-3">
            <div>
              <span className={`block text-xs uppercase tracking-wide ${mutedText}`}>Connection</span>
              <span className="block mt-1 text-sm font-medium">
                {scan.connection_name || (scan.m365_connection_id ? `Connection #${scan.m365_connection_id}` : '-')}
              </span>
            </div>
            <div>
              <span className={`block text-xs uppercase tracking-wide ${mutedText}`}>Started</span>
              <div className={`mt-1 text-sm font-semibold ${isDarkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                <RelativeTime value={scan.started_at || scan.created_at} />
              </div>
            </div>
            <div>
              <span className={`block text-xs uppercase tracking-wide ${mutedText}`}>Completed</span>
              {scan.finished_at || scan.completed_at ? (
                <div className={`mt-1 text-sm font-semibold ${isDarkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                  <RelativeTime value={scan.finished_at || scan.completed_at} />
                </div>
              ) : (
                <div className="mt-1 text-sm">
                  <div>{scan.status === 'pending' || scan.status === 'running' ? 'In progress' : '-'}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {(scan.status === 'pending' || scan.status === 'running') && (
          <div className={`${cardClass} p-6`}>
            <div className="flex gap-3 items-center">
              <Loader2 size={24} className="text-blue-500 animate-spin" />
              <div>
                <h3 className="text-lg font-semibold">Scan in Progress</h3>
                <p className={subtleText}>
                  {scan.status === 'pending'
                    ? 'Waiting to start...'
                    : `Evaluating controls... ${done} of ${summary.total} complete`}
                </p>
              </div>
            </div>

            <div className="mt-4">
              <div className={`h-2 w-full overflow-hidden rounded-full ${isDarkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                <div
                  className={`h-full rounded-full ${scan.status === 'running' ? 'bg-blue-500' : 'bg-amber-500'}`}
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <div className={`mt-2 flex items-center gap-2 text-sm ${mutedText}`}>
                <span>{done}/{summary.total} controls</span>
                <span>•</span>
                <span>{progressPercent}%</span>
              </div>
            </div>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className={`${cardClass} p-5`}>
            <div className="flex gap-3 items-center">
              <FileText size={20} className="text-blue-500" />
              <div>
                <div className="text-xl font-bold">{summary.total}</div>
                <div className={`text-sm ${mutedText}`}>Total Controls</div>
              </div>
            </div>
          </div>
          <div className={`${cardClass} p-5`}>
            <div className="flex gap-3 items-center">
              <CheckCircle size={20} className="text-emerald-500" />
              <div>
                <div className="text-xl font-bold">{summary.passed}</div>
                <div className={`text-sm ${mutedText}`}>Passed</div>
              </div>
            </div>
          </div>
          <div className={`${cardClass} p-5`}>
            <div className="flex gap-3 items-center">
              <XCircle size={20} className="text-rose-500" />
              <div>
                <div className="text-xl font-bold">{summary.failed}</div>
                <div className={`text-sm ${mutedText}`}>Failed</div>
              </div>
            </div>
          </div>
          <div className={`${cardClass} p-5`}>
            <div className="flex gap-3 items-center">
              <AlertTriangle size={20} className="text-amber-500" />
              <div>
                <div className="text-xl font-bold">{summary.errors}</div>
                <div className={`text-sm ${mutedText}`}>Errors</div>
              </div>
            </div>
          </div>
        </div>

        {results.length > 0 && (
          <div className={`${cardClass} p-6`}>
            <h2 className="text-xl font-semibold">Control Results</h2>
            <div className="mt-4 space-y-3">
              {results.map((result, index) => (
                <div
                  key={result.control_id || index}
                  className={`rounded-xl border p-4 ${isDarkMode ? 'bg-slate-900/30' : 'bg-slate-50'} ${getResultCardClass(result.status)}`}
                >
                  <div className="flex flex-wrap gap-3 justify-between items-center">
                    <div className="flex gap-2 items-center">
                      {getResultIcon(result.status)}
                      <span className={`text-xs font-semibold uppercase ${mutedText}`}>{result.control_id}</span>
                      <h4 className="font-semibold">{result.title || result.control_id}</h4>
                    </div>
                    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${getResultBadgeClass(result.status)}`}>
                      {getResultBadgeText(result.status)}
                    </span>
                  </div>
                  {result.description && <p className={`mt-2 text-sm ${subtleText}`}>{result.description}</p>}
                  {result.message && <p className={`mt-2 text-sm ${mutedText}`}>{result.message}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {scan.status === 'failed' && scan.error && (
          <div className="p-4 text-rose-500 rounded-xl border border-rose-500/30 bg-rose-500/10">
            <div className="flex gap-3 items-start">
              <AlertCircle size={20} />
              <div>
                <h4 className="font-semibold">Scan Failed</h4>
                <p className="text-sm">{scan.error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScanDetailPage;