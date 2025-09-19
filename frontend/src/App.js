import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Dashboard from './Dashboard';
import Sidebar from './components/Sidebar';
import Evidence from './components/EvidenceScanner/Evidence';
import StyleGuide from './components/StyleGuide';

function App() {
  const [sidebarWidth, setSidebarWidth] = useState(220);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const location = useLocation();

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

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="App">
      {location.pathname !== "/styleguide" && (
        <Sidebar onWidthChange={setSidebarWidth} isDarkMode={isDarkMode} />
      )}
      <Routes>
        <Route
          path="/"
          element={
            <Dashboard
              sidebarWidth={sidebarWidth}
              isDarkMode={isDarkMode}
              onThemeToggle={handleThemeToggle}
            />
          }
        />
        <Route
          path="/evidence-scanner"
          element={
            <Evidence
              sidebarWidth={sidebarWidth}
              isDarkMode={isDarkMode}
            />
          }
        />
        <Route path="/styleguide" element={<StyleGuide />} />
      </Routes>
    </div>
  );
}

export default App;