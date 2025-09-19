//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 17 September 2025
//Added theme support

import React, { useState } from "react";
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
const Sidebar = ({ onWidthChange, isDarkMode = true }) => {
  const [isExpanded, setIsExpanded] = useState(true); //Track whether sidebar is expanded
  const [activeItem, setActiveItem] = useState('home'); // Track active navigation item
  const [searchValue, setSearchValue] = useState(''); // Track search input value

  // Add this line right after the component declaration for debugging
console.log('Sidebar isDarkMode:', isDarkMode);
  //Event to toggle collapsed state and notify parents that the width has changed
  const toggleSidebar = () => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onWidthChange(newExpanded ? 220 : 80);
  };

  //Set active item to the key of whichever nav button was clicked
  const handleNavClick = (itemKey) => {
    setActiveItem(itemKey);
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
              <button className="search-toggle-button" onClick={toggleSidebar}>
                {/* arrow when open, hamburger when closed: */}
                ←
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
            <button className="toggle-button" onClick={toggleSidebar}>
              ☰
            </button>
          )}
        </div>

        {/* Main navigation area */}
        <ul className="nav-links">
          <NavButton 
            href={'/'} 
            name={'Home'} 
            icon={'🏠'} 
            isExpanded={isExpanded}
            isActive={activeItem === 'home'}
            onClick={() => handleNavClick('home')}
          />
          <NavButton 
            href={'/score'} 
            name={'Score'} 
            icon={'⭐'} 
            isExpanded={isExpanded}
            isActive={activeItem === 'score'}
            onClick={() => handleNavClick('score')}
          />
          <NavButton 
            href={'/recommendations'} 
            name={'Tasks'} 
            icon={'✓'} 
            isExpanded={isExpanded}
            isActive={activeItem === 'tasks'}
            onClick={() => handleNavClick('tasks')}
          />
          <NavButton 
            href={'/reports'} 
            name={'Reports'} 
            icon={'📄'} 
            isExpanded={isExpanded}
            isActive={activeItem === 'reports'}
            onClick={() => handleNavClick('reports')}
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
            onClick={() => handleNavClick('settings')}
          />
          <NavButton 
            href={'/account'} 
            name={'Account'} 
            icon={'👤'} 
            isExpanded={isExpanded}
            isActive={activeItem === 'account'}
            onClick={() => handleNavClick('account')}
          />
        </ul>
      </div>
    </nav>
  );
};

export default Sidebar;