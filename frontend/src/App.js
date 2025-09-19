import React, { useState, useEffect } from 'react';
import Dashboard from './Dashboard';
import Sidebar from './components/Sidebar';
import Evidence from './components/EvidenceScanner/Evidence';

function App() {
  const [sidebarWidth, setSidebarWidth] = useState(220);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [isDarkMode, setIsDarkMode] = useState(true);

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
    document.body.className = isDarkMode ? 'dark-theme' : 'light-theme';
  }, [isDarkMode]);

  const handleNavigation = (page) => {
    setCurrentPage(page);
  };

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
  };

  const renderCurrentPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return <Dashboard 
          sidebarWidth={sidebarWidth} 
          onNavigate={handleNavigation} 
          isDarkMode={isDarkMode}
          onThemeToggle={handleThemeToggle}
        />;
      case 'evidence-scanner':
        return <Evidence 
          sidebarWidth={sidebarWidth} 
          onNavigate={handleNavigation}
          isDarkMode={isDarkMode}
        />;
      default:
        return <Dashboard 
          sidebarWidth={sidebarWidth} 
          onNavigate={handleNavigation}
          isDarkMode={isDarkMode}
          onThemeToggle={handleThemeToggle}
        />;
    }
  };

  return (
    <div className="App">
      <Sidebar onWidthChange={setSidebarWidth}/>
      {renderCurrentPage()}
    </div>
  );
}

export default App;