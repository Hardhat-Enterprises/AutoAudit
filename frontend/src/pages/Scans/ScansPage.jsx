import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, CheckCircle, XCircle, Clock, Loader2, AlertCircle, PlayCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getScans, getConnections, getBenchmarks, createScan } from '../../api/client';
import { formatDateTimePartsAEST } from '../../utils/helpers';
import './ScansPage.css';

const ScansPage = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [scans, setScans] = useState([]);
  const [connections, setConnections] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    m365_connection_id: '',
    benchmark_key: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadScans = useCallback(async () => {
    try {
      const scansData = await getScans(token);
      setScans(scansData);
    } catch (err) {
      console.error('Failed to refresh scans:', err);
    }
  }, [token]);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const [scansData, connectionsData, benchmarksData] = await Promise.all([
          getScans(token),
          getConnections(token),
          getBenchmarks(token),
        ]);
        setScans(scansData);
        setConnections(connectionsData);
        setBenchmarks(benchmarksData);
      } catch (err) {
        setError(err.message || 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [token]);

  // Poll for scan updates every 5 seconds
  useEffect(() => {
    const hasPendingScans = scans.some(
      scan => scan.status === 'pending' || scan.status === 'running'
    );

    if (!hasPendingScans) return;

    const interval = setInterval(loadScans, 5000);
    return () => clearInterval(interval);
  }, [scans, loadScans]);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Parse the benchmark key (format: "framework|benchmark|version")
      const [framework, benchmark, version] = formData.benchmark_key.split('|');

      const newScan = await createScan(token, {
        m365_connection_id: parseInt(formData.m365_connection_id),
        framework,
        benchmark,
        version,
      });

      setScans(prev => [newScan, ...prev]);
      setFormData({ m365_connection_id: '', benchmark_key: '' });
      setShowForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create scan');
    } finally {
      setIsSubmitting(false);
    }
  }

  function getStatusIcon(status) {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="status-icon success" />;
      case 'failed':
        return <XCircle size={16} className="status-icon error" />;
      case 'running':
        return <Loader2 size={16} className="status-icon running spinning" />;
      default:
        return <Clock size={16} className="status-icon pending" />;
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
    return formatDateTimePartsAEST(dateString);
  }

  if (isLoading) {
    return (
      <div
        className={`scans-page ${isDarkMode ? 'dark' : 'light'}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: 'margin-left 0.4s ease, width 0.4s ease'
        }}
      >
        <div className="scans-container">
          <div className="loading-state">
            <Loader2 size={32} className="spinning" />
            <p>Loading scans...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`scans-page ${isDarkMode ? 'dark' : 'light'}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
      }}
    >
      <div className="scans-container">
        <div className="page-header">
          <div className="header-content">
            <Search size={24} />
            <div className="header-text">
              <h1>Compliance Scans</h1>
              <p>Run and manage compliance scans against your M365 connections</p>
            </div>
          </div>
          <button
            className="toolbar-button primary"
            onClick={() => setShowForm(!showForm)}
            disabled={connections.length === 0}
          >
            <Plus size={16} />
            <span>New Scan</span>
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {connections.length === 0 && !isLoading && (
          <div className="warning-banner">
            <AlertCircle size={18} />
            <span>You need to add a connection before you can run scans.</span>
          </div>
        )}

        {showForm && (
          <div className="scan-form-card">
            <h3>New Compliance Scan</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="m365_connection_id">Cloud Platform</label>
                  <select
                    id="m365_connection_id"
                    name="m365_connection_id"
                    value={formData.m365_connection_id}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                  >
                    <option value="">Select a cloud platform</option>
                    {connections.map(conn => (
                      <option key={conn.id} value={conn.id}>
                        {conn.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="benchmark_key">Benchmark</label>
                  <select
                    id="benchmark_key"
                    name="benchmark_key"
                    value={formData.benchmark_key}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                  >
                    <option value="">Select a benchmark</option>
                    {benchmarks.map(bench => (
                      <option
                        key={`${bench.framework}|${bench.slug}|${bench.version}`}
                        value={`${bench.framework}|${bench.slug}|${bench.version}`}
                      >
                        {bench.name} ({bench.version})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="toolbar-button secondary"
                  onClick={() => setShowForm(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="toolbar-button primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="spinning" />
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

        <div className="scans-list">
          {scans.length === 0 ? (
            <div className="empty-state">
              <Search size={48} />
              <h3>No scans yet</h3>
              <p>Run your first compliance scan to see results here.</p>
            </div>
          ) : (
            <table className="scans-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Benchmark</th>
                  <th>Connection</th>
                  <th>Started</th>
                  <th>Results</th>
                </tr>
              </thead>
              <tbody>
                {scans.map(scan => (
                  <tr
                    key={scan.id}
                    onClick={() => navigate(`/scans/${scan.id}`)}
                    className="scan-row"
                  >
                    <td>
                      <span className={`status-badge ${scan.status || 'pending'}`}>
                        {getStatusIcon(scan.status)}
                        {getStatusText(scan.status)}
                      </span>
                    </td>
                    <td>
                      <span className="benchmark-name">
                        {scan.benchmark || '-'}
                      </span>
                      <span className="benchmark-version">{scan.version || ''}</span>
                    </td>
                    <td>{scan.connection_name || (scan.m365_connection_id ? `Connection #${scan.m365_connection_id}` : '-')}</td>
                    <td>
                      {(() => {
                        const dt = formatDate(scan.started_at || scan.created_at);
                        if (dt === '-') return '-';
                        return (
                          <div className="datetime">
                            <div className="date">{dt.date}</div>
                            <div className="time">{dt.time}</div>
                          </div>
                        );
                      })()}
                    </td>
                    <td>
                      {scan.status === 'completed' || scan.status === 'running' ? (
                        <div className="results-summary">
                          <span className="passed">{scan.passed_count || 0} passed</span>
                          <span className="failed">{scan.failed_count || 0} failed</span>
                          {scan.status === 'running' && scan.total_controls > 0 && (
                            <span className="progress">
                              ({scan.passed_count + scan.failed_count + scan.error_count || 0}/{scan.total_controls})
                            </span>
                          )}
                        </div>
                      ) : (
                        '-'
                      )}
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
