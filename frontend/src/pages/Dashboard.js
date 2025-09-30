import React, { useState } from 'react';
import './Dashboard.css';
import ComplianceChart from '../components/ComplianceChart';
import Dropdown from '../components/Dropdown';
import { useNavigate } from "react-router-dom";
import { Card, Button } from "../ui"; // from src/pages → src/ui // add CTA Button



export default function Dashboard({ sidebarWidth = 220, isDarkMode, onThemeToggle }) {
  const navigate = useNavigate();
  
  const stats = [
    { label: 'Compliance Score', value: '85%', tone: 'good', subtitle: 'Overall security posture' },
    { label: 'Failed Checks', value: '12', tone: 'bad', subtitle: 'Requiring immediate attention' },
    { label: 'Last Scan', value: '2h ago', tone: 'muted', subtitle: 'Monday, August 14, 2025' },
    { label: 'Total Controls', value: '97', tone: 'muted', subtitle: 'CIS Rules Benchmark' }
  ];
  
  //helpers for tone-based text and icons
  const toneToText = (t) =>
  t === "good" ? "text-accent-good" :
  t === "warn" ? "text-accent-warn" :
  t === "bad"  ? "text-accent-bad"  :
                 "text-text-muted";

  const toneIcon = (t) => (t === "good" ? "✓" : t === "warn" ? "⚠" : t === "bad" ? "!" : "◉");


  const benchmarkOptions = [
    { value: 'apra-cps-234', label: 'APRA CPS 234 Information Security' },
    { value: 'essential-eight', label: 'Australian Cyber Security Centre Essential Eight' },
    { value: 'cis-google-cloud', label: 'CIS Google Cloud Platform Foundation' },
    { value: 'cis-microsoft-365', label: 'CIS Microsoft 365 Foundation' },
    { value: 'cobit', label: 'COBIT Control Objectives for Information and Related Technologies' },
    { value: 'gdpr', label: 'GDPR General Data Protection Regulation' },
    { value: 'hipaa', label: 'HIPAA Health Insurance Portability and Accountability Act' },
    { value: 'iso-27001', label: 'ISO 27001' },
    { value: 'nist-cybersecurity', label: 'NIST Cybersecurity Framework' },
    { value: 'pci-dss', label: 'PCI DSS (Payment Card Industry Data Security Standard)' },
    { value: 'soc-2', label: 'SOC 2 (Trust Services Criteria)' }, 
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
    navigate("/evidence-scanner");
  };

  return (
    <div className={`dashboard ${isDarkMode ? 'dark' : 'light'}`} style={{ 
      marginLeft: `${sidebarWidth}px`, 
      width: `calc(100vw - ${sidebarWidth}px)`,
      transition: 'margin-left 0.4s ease, width 0.4s ease'
    }}>
      <div className="dashboard-container">
        <header className="border-b border-border-subtle">
          <div className="container-max flex items-center justify-between gap-4 py-4">
            {/* Left: Logo + Title */}
            <div className="flex items-center gap-3">
              {/* Swap this for <img src="/AutoAudit.png" className="h-9 w-9 rounded-md" alt="AutoAudit Logo" /> later */}
              <div className="h-9 w-9 rounded-md bg-surface-2/80 flex items-center justify-center font-header text-sm">
                AA
              </div>
              <div>
                <h1 className="text-xl font-header leading-tight">AutoAudit</h1>
                <p className="text-text-muted text-sm font-body">Microsoft 365 Compliance Platform</p>
              </div>
            </div>
          
          {/* Keep toggle for now, reusing existing css classes */}
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
         </header>

        <div className="top-toolbar">
          <div className="toolbar-left">
            <span className="toolbar-label">Benchmark</span>
            <Dropdown
              value={selectedBenchmark}
              onChange={setSelectedBenchmark}
              options={benchmarkOptions}
              isDarkMode={isDarkMode}
            />
          </div>
          
          <div className="toolbar-right">
            <button className="toolbar-button secondary" onClick={handleExportReport}>
              Export Report
            </button>
            <button className="toolbar-button secondary" onClick={handleEvidenceScanner}>
              Evidence Scanner
            </button>
            {/* Trial new shared UI Button for primary CTA */}
            <Button variant="primary" size="md" onClick={handleRunNewScan}>
              Run New Scan
            </Button>
          </div>
        </div>


        {/* Stats section now changed to use Tailwind grid & Card */}
        <section className="container-max mt-6">
          <div className="tw-stats-grid">{/* uses Tailwind helper to avoid .stats-grid conflict */}
            {stats.map((s, i) => (
              <Card key={i} tone={s.tone}>
                <div className="flex items-start gap-3">
                  <div className={`text-lg ${toneToText(s.tone)}`}>{toneIcon(s.tone)}</div>
                  <div>
                    <p className="stat-label font-body text-text-strong text-lg ">{s.label}</p>
                    <p className={`stat-value font-header ${toneToText(s.tone)}`}>{s.value}</p>
                    <p className="stat-subtitle font-body">{s.subtitle}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* === PR4: Chart + Issues migrated to Tailwind tokens === */}
<section className="container-max mt-8">
  <div className="grid gap-6 lg:grid-cols-[2fr_0.9fr] items-stretch"> {/*2fr for chart, 0.9fr for issues*/}
    {/* Chart card (fills height) */}
    <div className="card flex flex-col">
      <div className="issue-header">
        <div className="issue-title">
          <span className="text-text-muted">◷</span>
          <h4 className="font-header">Scan Results</h4>
        </div>
        <Dropdown
          value={selectedChartType}
          onChange={setSelectedChartType}
          options={chartTypeOptions}
        />
      </div>
      <div className="flex-1">
        <div className="w-full h-full min-h-[420px]"> {/*increased min height for better appearance*/}
          <ComplianceChart
            chartType={selectedChartType}
            dataInput={[3, 9, 85]}
            isDarkMode={isDarkMode}
          />
        </div>
      </div>
    </div>

    {/* Issues column stacked vertically, make equal height using flex-1 */}
      <div className="issue-col">
        <Card tone="bad" className="flex-1">
          <div className="issue-header">
            <div className="issue-title">
              <span className="text-accent-bad">!</span>
              <h4 className="font-header text-xl">High Priority Issues</h4>
            </div>
            <span className="font-header text-accent-bad text-3xl">3</span>
          </div>
          <p className="issue-desc">Critical security gaps</p>
        </Card>

        <Card tone="warn" className="flex-1">
          <div className="issue-header">
            <div className="issue-title">
              <span className="text-accent-warn">⚬</span>
              <h4 className="font-header text-xl">Medium Priority Issues</h4>
            </div>
            <span className="font-header text-accent-warn text-3xl">9</span>
          </div>
          <p className="issue-desc">Important improvements needed</p>
        </Card>

        <Card tone="good" className="flex-1">
          <div className="issue-header">
            <div className="issue-title">
              <span className="text-accent-good">✓</span>
              <h4 className="font-header text-xl">Scan Status</h4>
            </div>
            <span className="font-header text-accent-good text-3xl">Complete</span>
          </div>
          <p className="issue-desc">Ready for next scan</p>
        </Card>
      </div>
    </div>
  </section>


        <div className='fit'>
          <section className="below-grid">
            <h3 className="section-title"></h3>
            <div className="content"></div>
          </section>
        </div>
      </div>
    </div>
  );
}
