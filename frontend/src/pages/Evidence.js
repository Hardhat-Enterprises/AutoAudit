import React, { useState, useEffect } from 'react';
import './Evidence.css';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const Evidence = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const [strategies, setStrategies] = useState([]);
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(true);
  const [strategiesError, setStrategiesError] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [userId, setUserId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/evidence/strategies`);
        if (!response.ok) {
          throw new Error('Failed to load strategies');
        }
        const payload = await response.json();
        const data = Array.isArray(payload) ? payload : [];
        setStrategies(data);
        setStrategiesError(data.length ? '' : 'No scanning strategies available yet.');
      } catch (err) {
        console.error('Unable to load strategies', err);
        setStrategiesError('Unable to load strategies from the backend.');
      } finally {
        setIsLoadingStrategies(false);
      }
    };

    fetchStrategies();
  }, []);

  const handleStrategyChange = (e) => {
    setSelectedStrategy(e.target.value);
    setError('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file || null);
    setError('');
  };

  const handleScan = async () => {
    setError('');
    setResults(null);
    
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
      const formData = new FormData();
      formData.append('strategy_name', selectedStrategy);
      formData.append('user_id', userId || 'user');
      formData.append('evidence', selectedFile);

      const response = await fetch(`${API_BASE_URL}/evidence/scan`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        let message = 'Scan failed. Please try again.';
        try {
          const payload = await response.json();
          if (payload?.detail) {
            message = payload.detail;
          }
        } catch {
          // ignore parse errors
        }
        throw new Error(message);
      }

      const payload = await response.json();
      setResults({
        strategy: payload?.strategy || selectedStrategy,
        file: payload?.file || selectedFile.name,
        findings: payload?.findings || [],
        reports: payload?.reports || [],
        note: payload?.note || ''
      });
    } catch (err) {
      console.error('Scan failed', err);
      setError(err.message || 'Scan failed. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  const getStatusClass = (status) => {
    switch ((status || '').toUpperCase()) {
      case 'PASS': return 'status-pass';
      case 'FAIL': return 'status-fail';
      case 'WARNING': return 'status-warning';
      default: return '';
    }
  };

  const selectedStrategyData = strategies.find(s => s.name === selectedStrategy);
  const noStrategiesAvailable = !isLoadingStrategies && strategies.length === 0;

  const resolveReportLink = (entry) => {
    if (!entry) return null;

    if (typeof entry === 'string') {
      const href = entry.startsWith('http')
        ? entry
        : `${API_BASE_URL}/evidence/reports/${entry}`;
      return { href, label: entry.toLowerCase().endsWith('.pdf') ? 'PDF' : 'Download' };
    }

    const filename = entry.filename || entry.name;
    if (entry.url) {
      const href = entry.url.startsWith('http')
        ? entry.url
        : `${API_BASE_URL}${entry.url}`;
      return { href, label: filename?.toLowerCase().endsWith('.pdf') ? 'PDF' : (filename || 'Download') };
    }

    if (filename) {
      const href = `${API_BASE_URL}/evidence/reports/${filename}`;
      return { href, label: filename.toLowerCase().endsWith('.pdf') ? 'PDF' : 'Download' };
    }

    return null;
  };

  return (
    <div 
      className={`evidence-scanner ${isDarkMode ? 'dark' : 'light'}`}
      style={{ 
        marginLeft: `${sidebarWidth}px`, 
        width: `calc(100vw - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
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
                disabled={isLoadingStrategies || noStrategiesAvailable || isScanning}
              >
                {isLoadingStrategies ? (
                  <option value="">Loading strategies...</option>
                ) : (
                  <>
                    <option value="">— select a strategy —</option>
                    {strategies.map((strategy) => (
                      <option key={strategy.name} value={strategy.name}>
                        {strategy.name}
                      </option>
                    ))}
                  </>
                )}
              </select>
              {selectedStrategyData && (
                <div className="form-help">{selectedStrategyData.description}</div>
              )}
              {strategiesError && (
                <div className="status-error">{strategiesError}</div>
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
              disabled={!selectedStrategy || isScanning || noStrategiesAvailable || isLoadingStrategies}
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
            
            {error && <span className="status-error">{error}</span>}
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <div className="results-card">
            <h3 className="results-header">Results</h3>
            
              <div className="results-meta">
                <div className="meta-tag">
                  <span>Strategy</span>
                  <span>{results.strategy || selectedStrategy}</span>
                </div>
                <div className="meta-tag">
                  <span>File</span>
                  <span>{results.file || selectedFile?.name}</span>
                </div>
              </div>

              {results.note && (
                <div className="form-help">{results.note}</div>
              )}

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
                    <th>Evidence Extract</th>
                    <th>Report</th>
                  </tr>
                </thead>
                <tbody>
                  {results.findings.map((finding, index) => {
                    const reportLink = resolveReportLink(results.reports?.[index]);
                    return (
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
                        {Array.isArray(finding.evidence) 
                          ? finding.evidence.map((item, i) => (
                              <div key={i}>{item}</div>
                            ))
                          : finding.evidence
                        }
                      </td>
                      <td>
                        {reportLink ? (
                          <a 
                            href={reportLink.href} 
                            className="evidence-link"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {reportLink.label}
                          </a>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  )})}
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
