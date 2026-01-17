import React, { useState, useEffect, useCallback } from 'react';
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
import { useAuth } from '../../context/AuthContext';
import { getScan } from '../../api/client';
import './ScanDetailPage.css';

function compareControlIdAscending(a, b) {
  const aId = (a?.control_id || '').toString();
  const bId = (b?.control_id || '').toString();
  const aParts = aId.split('.').map(s => Number.parseInt(s, 10));
  const bParts = bId.split('.').map(s => Number.parseInt(s, 10));

  const len = Math.max(aParts.length, bParts.length);
  for (let i = 0; i < len; i++) {
    const av = Number.isFinite(aParts[i]) ? aParts[i] : -1;
    const bv = Number.isFinite(bParts[i]) ? bParts[i] : -1;
    if (av !== bv) return av - bv;
  }
  return aId.localeCompare(bId);
}

const ScanDetailPage = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [scan, setScan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadScan = useCallback(async () => {
    try {
      const scanData = await getScan(token, scanId);
      setScan(scanData);
      return scanData;
    } catch (err) {
      setError(err.message || 'Failed to load scan');
      return null;
    }
  }, [token, scanId]);

  useEffect(() => {
    async function initialLoad() {
      setIsLoading(true);
      await loadScan();
      setIsLoading(false);
    }
    initialLoad();
  }, [loadScan]);

  // Poll for updates every 3 seconds while pending/running
  useEffect(() => {
    if (!scan || scan.status === 'completed' || scan.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      const updatedScan = await loadScan();
      if (updatedScan?.status === 'completed' || updatedScan?.status === 'failed') {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [scan, loadScan]);

  function getStatusIcon(status) {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} className="status-icon success" />;
      case 'failed':
        return <XCircle size={20} className="status-icon error" />;
      case 'running':
        return <Loader2 size={20} className="status-icon running spinning" />;
      default:
        return <Clock size={20} className="status-icon pending" />;
    }
  }

  function getStatusText(status) {
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

  function formatDate(dateString) {
    if (!dateString) return '-';
    const d = new Date(dateString);
    if (Number.isNaN(d.getTime())) return '-';
    // Force "DD Mon YYYY" and show timezone explicitly.
    return d.toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  function formatTime(dateString) {
    if (!dateString) return '-';
    const d = new Date(dateString);
    if (Number.isNaN(d.getTime())) return '-';

    function getLocalTimeZoneAbbr(dateObj) {
      const longName = new Intl.DateTimeFormat('en-US', {
        timeZoneName: 'long',
      }).formatToParts(dateObj).find(p => p.type === 'timeZoneName')?.value;

      if (!longName) return '';
      if (longName ==='India Standard Time') return 'IST';
      if (longName === 'Coordinated Universal Time') return 'UTC';
      if (longName === 'Greenwich Mean Time') return 'GMT';
      if (longName === 'Universal Coordinated Time') return 'UTC';

      const embedded = longName.match(/\b[A-Z]{2,6}\b/)?.[0];
      if (embedded) return embedded;

      const words = longName
        .replace(/[^A-Za-z\s]/g, ' ')
        .split(/\s+/)
        .filter(Boolean);
      const trimmed = words.filter((w, idx) => !(idx === words.length - 1 && w.toLowerCase() === 'time'));
      const abbr = trimmed.map(w => w[0]).join('').toUpperCase();
      return abbr.length >= 2 ? abbr : '';
    }

    const timeCore = new Intl.DateTimeFormat('en-GB', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3,
      hour12: true,
    }).format(d);
    const tzAbbr = getLocalTimeZoneAbbr(d);
    return tzAbbr ? `${timeCore} ${tzAbbr}` : timeCore;
  }

  function getResultIcon(status) {
    switch (status) {
      case 'passed':
        return <CheckCircle size={16} className="result-icon pass" />;
      case 'failed':
        return <XCircle size={16} className="result-icon fail" />;
      case 'error':
        return <AlertTriangle size={16} className="result-icon error" />;
      case 'pending':
        return <Clock size={16} className="result-icon pending" />;
      default:
        return <AlertCircle size={16} className="result-icon unknown" />;
    }
  }

  function getResultBadgeText(status) {
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

  if (isLoading) {
    return (
      <div
        className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: 'margin-left 0.4s ease, width 0.4s ease'
        }}
      >
        <div className="scan-detail-container">
          <div className="loading-state">
            <Loader2 size={32} className="spinning" />
            <p>Loading scan details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div
        className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: 'margin-left 0.4s ease, width 0.4s ease'
        }}
      >
        <div className="scan-detail-container">
          <div className="error-state">
            <AlertCircle size={48} />
            <h3>Failed to load scan</h3>
            <p>{error || 'Scan not found'}</p>
            <button className="toolbar-button secondary" onClick={() => navigate('/scans')}>
              <ArrowLeft size={16} />
              <span>Back to Scans</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Build summary from scan counts (API returns these directly)
  const summary = {
    total: scan.total_controls || 0,
    passed: scan.passed_count || 0,
    failed: scan.failed_count || 0,
    errors: scan.error_count || 0,
    pending: (scan.total_controls || 0) - (scan.passed_count || 0) - (scan.failed_count || 0) - (scan.error_count || 0) - (scan.skipped_count || 0),
  };
  const done = summary.passed + summary.failed + summary.errors + (scan.skipped_count || 0);
  const progressPercent =
    summary.total > 0
      ? Math.min(100, Math.round((done / summary.total) * 100))
      : scan.status === 'completed' ? 100: 0;
  const results = (scan.results || [])
    .filter(r => (r?.status || '').toLowerCase() !== 'skipped')
    .slice()
    .sort(compareControlIdAscending);

  return (
    <div
      className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
      }}
    >
      <div className="scan-detail-container">
        <div className="page-header">
          <button className="back-button" onClick={() => navigate('/scans')}>
            <ArrowLeft size={20} />
            <span>Back to Scans</span>
          </button>
        </div>

        <div className="scan-header-card">
          <div className="scan-header-content">
            <div className="scan-icon">
              <Shield size={32} />
            </div>
            <div className="scan-info">
              <h1>{scan.benchmark || 'Compliance Scan'}</h1>
              <p>{scan.version || ''}</p>
            </div>
            <span className={`status-badge large ${scan.status || 'pending'}`}>
              {getStatusIcon(scan.status)}
              {getStatusText(scan.status)}
            </span>
          </div>

          <div className="scan-meta">
            <div className="meta-item">
              <span className="meta-label">Connection</span>
              <span className="meta-value">
                {scan.connection_name || (scan.m365_connection_id ? `Connection #${scan.m365_connection_id}` : '-')}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Started</span>
              <div className="meta-value">
                <div className="meta-date">{formatDate(scan.started_at || scan.created_at)}</div>
                <div className="meta-time">{formatTime(scan.started_at || scan.created_at)}</div>
              </div>
            </div>
            <div className="meta-item">
              <span className="meta-label">Completed</span>
              {scan.finished_at || scan.completed_at ? (
                <div className="meta-value">
                  <div className="meta-date">{formatDate(scan.finished_at || scan.completed_at)}</div>
                  <div className="meta-time">{formatTime(scan.finished_at || scan.completed_at)}</div>
                </div>
              ) : (
                <div className="meta-value">
                  <div className="meta-date">
                    {(scan.status === 'pending' || scan.status === 'running') ? 'In progress' : '-'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {(scan.status === 'pending' || scan.status === 'running') && (
          <div className="progress-card">
            <div className="progress-content">
              <Loader2 size={24} className="spinning" />
              <div className="progress-text">
                <h3>Scan in Progress</h3>
                <p>
                  {scan.status === 'pending'
                    ? 'Waiting to start...'
                    : `Evaluating controls... ${done} of ${summary.total} complete`}
                </p>
              </div>
            </div>

            <div className="scan-progress-bar">
              <div className="scan-progress-track">
                <div
                  className={`scan-progress-fill ${scan.status || 'pending'}`}
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <div className="scan-progress-meta">
                <span>{done}/{summary.total} controls</span>
                <span className="scan-progress-sep">•</span>
                <span>{progressPercent}%</span>
              </div>
            </div>
          </div>
        )}

        <div className="stats-grid">
          <div className="stat-card total">
            <div className="stat-icon">
              <FileText size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-value">{summary.total}</span>
              <span className="stat-label">Total Controls</span>
            </div>
          </div>
          <div className="stat-card passed">
            <div className="stat-icon">
              <CheckCircle size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-value">{summary.passed}</span>
              <span className="stat-label">Passed</span>
            </div>
          </div>
          <div className="stat-card failed">
            <div className="stat-icon">
              <XCircle size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-value">{summary.failed}</span>
              <span className="stat-label">Failed</span>
            </div>
          </div>
          <div className="stat-card errors">
            <div className="stat-icon">
              <AlertTriangle size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-value">{summary.errors}</span>
              <span className="stat-label">Errors</span>
            </div>
          </div>
        </div>

        {results.length > 0 && (
          <div className="results-section">
            <h2>Control Results</h2>
            <div className="results-list">
              {results.map((result, index) => (
                <div
                  key={result.control_id || index}
                  className={`result-card ${result.status || 'unknown'}`}
                >
                  <div className="result-header">
                    <div className="result-title">
                      {getResultIcon(result.status)}
                      <span className="control-id">{result.control_id}</span>
                      <h4>{result.title || result.control_id}</h4>
                    </div>
                    <span className={`result-badge ${result.status || 'unknown'}`}>
                      {getResultBadgeText(result.status)}
                    </span>
                  </div>
                  {result.description && (
                    <p className="result-description">{result.description}</p>
                  )}
                  {result.message && (
                    <p className="result-message">{result.message}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {scan.status === 'failed' && scan.error && (
          <div className="error-card">
            <AlertCircle size={20} />
            <div className="error-content">
              <h4>Scan Failed</h4>
              <p>{scan.error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScanDetailPage;
