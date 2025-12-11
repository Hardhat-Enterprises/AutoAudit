//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 17 September 2025
//Added theme support

import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import './Sidebar.css';


//Button component that we use throughout the sidebar
//Parameters:
//href - link reference
//name - text to display in expanded view
//icon - text to display in collapsed view

const NavButton = ({ href, name, icon, isExpanded, isActive = false, onClick }) => {
  const handleClick = (clickEvent) => {
    if (onClick) {
      clickEvent.preventDefault();
      onClick(clickEvent);
    }
  };

  return (
    <li className="nav-item">
      <a
        className={`nav-link ${isExpanded ? 'expanded' : ''} ${isActive ? 'active' : ''}`}
        href={href}
        onClick={handleClick}
      >
        <span className="nav-icon">{icon}</span>
        {isExpanded && <span className="nav-text">{name}</span>}
      </a>
    </li>
  );
};

// Main sidebar component
const Sidebar = ({ onWidthChange = () => {}, isDarkMode = true }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isExpanded, setIsExpanded] = useState(true); //Track whether sidebar is expanded
  const [searchValue, setSearchValue] = useState(''); // Track search input value

  // Determine active item based on current route
  const getActiveItem = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'home';
    if (path === '/cloud-platforms') return 'cloud-platforms';
    if (path.startsWith('/scans')) return 'scans';
    if (path === '/evidence-scanner') return 'tasks';
    if (path === '/reports') return 'reports';
    if (path === '/settings') return 'settings';
    if (path === '/account') return 'account';
    return 'home';
  };

  const activeItem = getActiveItem();

  //Event to toggle collapsed state and notify parents that the width has changed
  const toggleSidebar = () => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onWidthChange(newExpanded ? 220 : 80);
  };

  //Navigate to the specified route
  const handleNavClick = (itemKey, route) => {
    navigate(route);
  };

  //Once search is functional, this search value should be used as the search parameter. Just a placeholder for now, though.
  const handleSearchChange = (typed) => {
    setSearchValue(typed.target.value);
  };

  return (          
    <nav className={`sidebar ${isDarkMode ? 'dark' : 'light'}`} style={{'--sidebar-width': isExpanded ? '220px' : '80px'}}>
      <div className="sidebar-content">       
        <div className="search-container">
          {/* only display when the navbar is expanded! */}
          {isExpanded ? (
            <div className="search-bar">
              <button className="search-toggle-button" onClick={toggleSidebar} aria-label="Collapse sidebar">
                ×
              </button>
              <input
                type="text"
                placeholder="Search..."
                value={searchValue}
                onChange={handleSearchChange}
                className="search-input"
              />
              <span className="search-icon">🔍</span>
            </div>
          ) : (
            <button className="toggle-button" onClick={toggleSidebar} aria-label="Expand sidebar">
              ☰
            </button>
          )}
        </div>

        {/* Main navigation area */}
        <ul className="nav-links">
          <NavButton
            href={'/dashboard'}
            name={'Dashboard'}
            icon={'🏠'}
            isExpanded={isExpanded}
            isActive={activeItem === 'home'}
            onClick={() => handleNavClick('home', '/dashboard')}
          />
          <NavButton
            href={'/cloud-platforms'}
            name={'Cloud Platforms'}
            icon={'☁'}
            isExpanded={isExpanded}
            isActive={activeItem === 'cloud-platforms'}
            onClick={() => handleNavClick('cloud-platforms', '/cloud-platforms')}
          />
          <NavButton
            href={'/scans'}
            name={'Scans'}
            icon={'🔍'}
            isExpanded={isExpanded}
            isActive={activeItem === 'scans'}
            onClick={() => handleNavClick('scans', '/scans')}
          />
          <NavButton
            href={'/evidence-scanner'}
            name={'Evidence'}
            icon={'✓'}
            isExpanded={isExpanded}
            isActive={activeItem === 'tasks'}
            onClick={() => handleNavClick('tasks', '/evidence-scanner')}
          />
          <NavButton
            href={'/reports'}
            name={'Reports'}
            icon={'📄'}
            isExpanded={isExpanded}
            isActive={activeItem === 'reports'}
            onClick={() => handleNavClick('reports', '/reports')}
          />
        </ul>
        
        {/* Settings section at bottom */}
        <ul className="nav-settings">
          <NavButton
            href={'/settings'}
            name={'Settings'}
            icon={'⚙'}
            isExpanded={isExpanded}
            isActive={activeItem === 'settings'}
            onClick={() => handleNavClick('settings', '/settings')}
          />
          <NavButton
            href={'/account'}
            name={'Account'}
            icon={'👤'}
            isExpanded={isExpanded}
            isActive={activeItem === 'account'}
            onClick={() => handleNavClick('account', '/account')}
          />
        </ul>
      </div>
    </nav>
  );
};

export default Sidebar;
