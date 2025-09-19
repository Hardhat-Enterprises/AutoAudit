import React, { useState } from 'react';
import './Dashboard.css';
import ComplianceChart from './components/ComplianceChart';
import Dropdown from './components/Dropdown';

export default function Dashboard({ sidebarWidth = 220, onNavigate, isDarkMode, onThemeToggle }) {
  const stats = [
    { label: 'Compliance Score', value: '85%', className: 'emerald', subtitle: 'Overall security posture' },
    { label: 'Failed Checks', value: '12', className: 'orange', subtitle: 'Requiring immediate attention' },
    { label: 'Last Scan', value: '2h ago', className: 'gray', subtitle: 'Monday, August 14, 2025' },
    { label: 'Total Controls', value: '97', className: 'gray', subtitle: 'CIS Rules Benchmark' }
  ];

  const benchmarkOptions = [
    { value: 'cis-google-cloud', label: 'CIS Google Cloud Platform Foundation' },
    { value: 'cis-microsoft-365', label: 'CIS Microsoft 365 Foundation' },
    { value: 'nist-cybersecurity', label: 'NIST Cybersecurity Framework' },
    { value: 'iso-27001', label: 'ISO 27001' },
  ];

  const chartTypeOptions = [
    { value: 'doughnut', label: 'Doughnut Chart' },
    { value: 'pie', label: 'Pie Chart' },
  ];
    
  const [selectedChartType, setSelectedChartType] = useState('doughnut');
  const [selectedBenchmark, setSelectedBenchmark] = useState('cis-google-cloud');

  const handleExportReport = () => {
    console.log('Exporting report...');
  };

  const handleRunNewScan = () => {
    console.log('Running scan...');
  };

  const handleEvidenceScanner = () => {
    onNavigate('evidence-scanner');
  };

  return (
    <div className={`dashboard ${isDarkMode ? 'dark' : 'light'}`} style={{ 
      marginLeft: `${sidebarWidth}px`, 
      width: `calc(100vw - ${sidebarWidth}px)`,
      transition: 'margin-left 0.4s ease, width 0.4s ease'
    }}>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-content">
            <div className="logo-container">
              <img 
                src="/AutoAudit.png" 
                alt="AutoAudit Logo" 
                className="logo-image"
              />
            </div>
            <div className="header-text">
              <h1>AutoAudit</h1>
              <p>Microsoft 365 Compliance Platform</p>
            </div>
          </div>
          
          <div className="theme-toggle">
            <span className="theme-label">🌞</span>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={isDarkMode} 
                onChange={onThemeToggle}
                aria-label="Toggle theme"
              />
              <span className="slider"></span>
            </label>
            <span className="theme-label">🌙</span>
          </div>
        </div>

        <div className="top-toolbar">
          <div className="toolbar-left">
            <span className="toolbar-label">Benchmark</span>
            <Dropdown
              value={selectedBenchmark}
              onChange={setSelectedBenchmark}
              options={benchmarkOptions}
            />
          </div>
          
          <div className="toolbar-right">
            <button className="toolbar-button secondary" onClick={handleExportReport}>
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

        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className={`stat-card ${stat.className}`}>
              <div className="stat-content">
                <div className="stat-info">
                  <div className="stat-icon">
                    {stat.className === 'emerald' && <span>✓</span>}
                    {stat.className === 'orange' && <span>⚠</span>}
                    {stat.className === 'gray' && <span>🕐</span>}
                  </div>
                  <div className="stat-text">
                    <p className="stat-label">{stat.label}</p>
                    <p className="stat-value">{stat.value}</p>
                    <p className="stat-subtitle">{stat.subtitle}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="main-grid">
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
              />
            </div>
            <ComplianceChart chartType={selectedChartType} dataInput={[3, 9, 85]} isDarkMode={isDarkMode} />
          </div>

          <div className="issues-section">
            <div className="issue-card red">
              <div className="issue-header">
                <div className="issue-title">
                  <span className="issue-icon">!</span>
                  <h4>High Priority Issues</h4>
                </div>
                <span className="issue-count">3</span>
              </div>
              <p className="issue-desc">Critical security gaps</p>
            </div>

            <div className="issue-card orange">
              <div className="issue-header">
                <div className="issue-title">
                  <span className="issue-icon">⚬</span>
                  <h4>Medium Priority Issues</h4>
                </div>
                <span className="issue-count">9</span>
              </div>
              <p className="issue-desc">Important improvements needed</p>
            </div>

            <div className="issue-card emerald">
              <div className="issue-header">
                <div className="issue-title">
                  <span className="issue-icon">✓</span>
                  <h4>Scan Status</h4>
                </div>
                <span className="issue-status">Complete</span>
              </div>
              <p className="issue-desc">Ready for next scan</p>
            </div>
          </div>
        </div>

        <div className='fit'>
          <section className="below-grid">
            <h3 className="section-title"></h3>
            <div className="content"></div>
          </section>

          <section className="bottom-grid">
            <h3 className="section-title"></h3>
            <div className="content"></div>
          </section>
        </div>
      </div>
    </div>
  );
}