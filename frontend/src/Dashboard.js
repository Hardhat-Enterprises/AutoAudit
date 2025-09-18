
import React, { useState, useEffect } from 'react';

import './Dashboard.css';
import ComplianceChart from './components/ComplianceChart';
import Dropdown from './components/Dropdown';


export default function Dashboard({ sidebarWidth = 220 }) {
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark mode

  // Load theme preference from localStorage on component mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  // Save theme preference to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    // Add theme class to document body for global styling
    document.body.className = isDarkMode ? 'dark-theme' : 'light-theme';
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const stats = [
    { label: 'Compliance Score', value: '85%', className: 'emerald', subtitle: 'Overall security posture' },
    { label: 'Failed Checks', value: '12', className: 'orange', subtitle: 'Requiring immediate attention' },
    { label: 'Last Scan', value: '2h ago', className: 'gray', subtitle: 'Monday, August 14, 2025' },
    { label: 'Total Controls', value: '97', className: 'gray', subtitle: 'CIS Rules Benchmark' }
  ];

  const issues = [
    { label: 'High Priority Issues', count: '3', className: 'red', desc: 'Critical security gaps' },
    { label: 'Medium Priority Issues', count: '9', className: 'orange', desc: 'Important improvements needed' },
    { label: 'Scan Status', status: 'Complete', className: 'emerald', desc: 'Ready for next scan' }
  ];

  //Options for chart type selection. For now only doughnut and pie chart are available. 
    const chartTypeOptions = [
    { value: 'doughnut', label: 'Doughnut Chart' },
    { value: 'pie', label: 'Pie Chart' },
  ];

  const [selectedChartType, setSelectedChartType] = useState('doughnut'); //Default to a doughnut chart. 

  //The inline styling below adjusts the dashboard area to fit the width that is the difference between the total screen space and the current width of the navbar, this allows it to move when the navbar is collapsed or expanded.

  return (

  <div className={`dashboard ${isDarkMode ? 'dark' : 'light'}`} style={{ 
    marginLeft: `${sidebarWidth}px`, 
    width: `calc(100vw - ${sidebarWidth}px)`,
    transition: 'margin-left 0.4s ease, width 0.4s ease'
  }}>>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-content">
            <div className="logo-small">AA</div>
            <div className="header-text">
              <h1>AutoAudit</h1>
              <p>Microsoft 365 Compliance Platform</p>
            </div>
          </div>
          
          {/* Theme Toggle Switch */}
          <div className="theme-toggle">
            <span className="theme-label">🌞</span>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={isDarkMode} 
                onChange={toggleTheme}
                aria-label="Toggle theme"
              />
              <span className="slider"></span>
            </label>
            <span className="theme-label">🌙</span>

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
                    <span className="issue-icon">◷</span>
                    <h4>Scan Results</h4>
              </div>
              <Dropdown
                value={selectedChartType}
                onChange={setSelectedChartType}
                options={chartTypeOptions}
              />
            </div>
            <ComplianceChart chartType={selectedChartType} dataInput = {[3, 9, 85]}></ComplianceChart>

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
                <span className="issue-icon">◐</span>
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
          <div className="compliance-section">
            
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
                  <span className="issue-icon">◐</span>
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
          <span className="issue-status">Complete</span>
        </div>
        <p className="issue-desc">Ready for next scan</p>
      </div>
    </div>
  </div>
</div>

      <div className='fit'>
        <section className="below-grid">
          <h3 className="section-title"></h3>
          <div className="content">
            
          </div>
        </section>

        <section className="bottom-grid">
          <h3 className="section-title"></h3>
          <div className="content">
            
          </div>
        </section>
      </div>
    </div>
  );
}