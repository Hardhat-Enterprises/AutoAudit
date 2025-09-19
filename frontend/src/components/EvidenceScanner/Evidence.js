import React, { useState, useEffect } from 'react';
import './Evidence.css';

const Evidence = ({ sidebarWidth = 220, onNavigate, isDarkMode = true }) => {
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [userId, setUserId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Mock strategies data
  const strategies = [
    { name: 'CIS Microsoft 365 Audit', description: 'Comprehensive Microsoft 365 security assessment based on CIS benchmarks' },
    { name: 'NIST Compliance Check', description: 'NIST Cybersecurity Framework compliance verification' },
    { name: 'ISO 27001 Assessment', description: 'ISO 27001 information security management system audit' },
    { name: 'SOC 2 Readiness', description: 'SOC 2 Type II compliance preparation and gap analysis' },
    { name: 'GDPR Compliance Scan', description: 'General Data Protection Regulation compliance assessment' }
  ];

  // Mock results data
  const mockResults = {
    findings: [
      {
        test_id: 'CIS-001',
        sub_strategy: 'Identity & Access',
        detected_level: 'High',
        pass_fail: 'FAIL',
        priority: 'Critical',
        recommendation: 'Enable multi-factor authentication for all admin accounts',
        evidence: ['Admin account "admin@company.com" does not have MFA enabled', 'Found 3 admin accounts without MFA']
      },
      {
        test_id: 'CIS-002',
        sub_strategy: 'Data Protection',
        detected_level: 'Medium',
        pass_fail: 'FAIL',
        priority: 'High',
        recommendation: 'Implement data loss prevention policies',
        evidence: ['No DLP policies found', 'Sensitive data sharing detected']
      },
      {
        test_id: 'CIS-003',
        sub_strategy: 'Access Management',
        detected_level: 'Low',
        pass_fail: 'PASS',
        priority: 'Medium',
        recommendation: 'Continue monitoring access patterns',
        evidence: ['Access controls properly configured', 'Regular access reviews in place']
      },
      {
        test_id: 'CIS-004',
        sub_strategy: 'Audit Logging',
        detected_level: 'Medium',
        pass_fail: 'WARNING',
        priority: 'Medium',
        recommendation: 'Extend audit log retention period',
        evidence: ['Audit logs retained for 90 days', 'Recommended retention: 1 year']
      },
      {
        test_id: 'CIS-005',
        sub_strategy: 'Email Security',
        detected_level: 'High',
        pass_fail: 'FAIL',
        priority: 'Critical',
        recommendation: 'Configure advanced threat protection',
        evidence: ['ATP not enabled', 'Phishing protection insufficient']
      }
    ],
    reports: ['report-001.pdf', 'report-002.pdf', 'report-003.pdf', 'report-004.pdf', 'report-005.pdf']
  };

  const handleStrategyChange = (e) => {
    setSelectedStrategy(e.target.value);
    setError('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setError('');
  };

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
    
    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 3000)); // 3 second delay
      setResults(mockResults);
    } catch (err) {
      setError('Scan failed. Please try again.');
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

  const selectedStrategyData = strategies.find(s => s.name === selectedStrategy);

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
        {/* Back Button */}
        <div className="nav-breadcrumb">
          <span className="nav-link" onClick={() => onNavigate('dashboard')}>
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
              >
                <option value="">— select a strategy —</option>
                {strategies.map((strategy, index) => (
                  <option key={index} value={strategy.name}>
                    {strategy.name}
                  </option>
                ))}
              </select>
              {selectedStrategyData && (
                <div className="form-help">{selectedStrategyData.description}</div>
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
              disabled={!selectedStrategy}
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
                    <th>Evidence Extract</th>
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
                        {Array.isArray(finding.evidence) 
                          ? finding.evidence.map((item, i) => (
                              <div key={i}>{item}</div>
                            ))
                          : finding.evidence
                        }
                      </td>
                      <td>
                        {results.reports[index] && (
                          <a 
                            href={`#${results.reports[index]}`} 
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