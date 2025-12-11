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

const ScanDetailPage = ({ isDarkMode }) => {
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
    return new Date(dateString).toLocaleString();
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
      <div className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}>
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
      <div className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}>
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
  const results = scan.results || [];

  return (
    <div className={`scan-detail-page ${isDarkMode ? 'dark' : 'light'}`}>
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
              <span className="meta-value">{scan.connection_name || '-'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Started</span>
              <span className="meta-value">{formatDate(scan.created_at)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Completed</span>
              <span className="meta-value">{formatDate(scan.completed_at)}</span>
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
                    : `Evaluating controls... ${summary.passed + summary.failed + summary.errors} of ${summary.total} complete`}
                </p>
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
