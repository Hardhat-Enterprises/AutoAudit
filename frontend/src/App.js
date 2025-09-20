import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Evidence from './pages/Evidence';
import StyleGuide from './pages/StyleGuide';

// NOTE: No need to import './styles/global.css' here.
// It is imported once in index.js for the whole app.

function App() {
  const [sidebarWidth, setSidebarWidth] = useState(220);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const location = useLocation();

    // Save theme and apply the correct class at the ROOT element (<html>)
  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');

    // Use <html> to switch tokens: add/remove .light per tokens.css
    const root = document.documentElement; // <html>
    if (isDarkMode) {
      root.classList.remove('light');      // dark = default tokens on :root
    } else {
      root.classList.add('light');         // light = override tokens under .light
    }

    // document.body.className = isDarkMode ? 'dark-theme' : 'light-theme';
    // Removed as we no longer toggle classes on <body>; tokens.css expects .light on <html>
  }, [isDarkMode]);

  // Save theme preference to localStorage whenever it changes
  // useEffect(() => {
  // localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');

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
