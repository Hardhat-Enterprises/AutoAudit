//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 17 September 2025
//Added theme support

import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Cloud,
  FileSearch,
  ShieldCheck,
  FileText,
  Settings,
  User,
  Menu,
  ArrowLeft,
  Search,
} from "lucide-react";
import "./Sidebar.css";
import { X } from "lucide-react";


//Button component that we use throughout the sidebar
//Parameters:
//href - link reference
//name - text to display in expanded view
//icon - text to display in collapsed view

const NavButton = ({ href, name, icon: Icon, isExpanded, isActive = false, onClick }) => {
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
        <span className="nav-icon" aria-hidden="true">
          <Icon size={18} strokeWidth={2.2} />
        </span>
        {isExpanded && <span className="nav-text">{name}</span>}
      </a>
    </li>
  );
};

// Main sidebar component
const SIDEBAR_EXPANDED_KEY = "sidebarExpanded";

const Sidebar = ({ onWidthChange = () => {}, isDarkMode = true }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const [isExpanded, setIsExpanded] = useState(() => {
    if (typeof window === "undefined") return true;
    try {
      const stored = window.localStorage.getItem(SIDEBAR_EXPANDED_KEY);
      if (stored === null) return true;
      return stored === "true";
    } catch {
      return true;
    }
  }); // Track whether sidebar is expanded (persisted)

  const [searchValue, setSearchValue] = useState(''); // Track search input value

  // Track whether the sidebar is hidden on mobile/tablet
  const [isHidden, setIsHidden] = useState(false);

  // Track whether the current viewport is mobile or tablet
  const [isMobile, setIsMobile] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.innerWidth <= 1024;
  });

  // Detect screen size changes for mobile/tablet behavior
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 1024;
      setIsMobile(mobile);

      // Only force-show sidebar again when leaving mobile
      if (!mobile) {
        setIsHidden(false);
      }
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

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
    if (typeof window !== "undefined") {
      try {
        window.localStorage.setItem(SIDEBAR_EXPANDED_KEY, String(newExpanded));
      } catch {
        // ignore storage errors (private mode, blocked, etc.)
      }
    }
  };

  //Navigate to the specified route
  const handleNavClick = (itemKey, route) => {
    navigate(route);

    if (isMobile) {
      setIsHidden(true);
    }
  };

  //Once search is functional, this search value should be used as the search parameter. Just a placeholder for now, though.
  const handleSearchChange = (typed) => {
    setSearchValue(typed.target.value);
  };

  return (          
    <>
      <nav className={`sidebar ${isDarkMode ? 'dark' : 'light'} ${isHidden ? 'sidebar--hidden' : ''}`} style={{ '--sidebar-width': isExpanded ? '220px' : '80px' }}>
        <div className="sidebar-content">
          {/* This closes the sidebar for mobile and tablet views */}
          {isMobile && !isHidden && (
            <button className="close-sidebar-button" onClick={() => setIsHidden(true)} aria-label="Close sidebar">
              <X size={20} strokeWidth={2.2} />
            </button>
          )}

          <div className="search-container">
            {isExpanded ? (
              <>
                {/* The collapse arrow is only displayed when the sidebar is expanded (e.g. 1024px) */}
                <div className="search-toggle-wrapper">
                  <button className="search-toggle-button" onClick={toggleSidebar} aria-label="Collapse sidebar">
                    <ArrowLeft size={18} />
                  </button>
                </div>

                <div className="search-bar">
                  <input className="search-input" type="text" placeholder="Search..." value={searchValue} onChange={handleSearchChange}/>
                  <span className="search-icon">
                    <Search size={16} />
                  </span>
                </div>
              </>
            ) : (
              <button className="toggle-button" onClick={toggleSidebar}aria-label="Expand sidebar">
                <Menu size={18} strokeWidth={2.2} />
              </button>
            )}
          </div>

          {/* Main navigation area */}
          <ul className="nav-links">
            <NavButton
              href={"/dashboard"}
              name={"Dashboard"}
              icon={LayoutDashboard}
              isExpanded={isExpanded}
              isActive={activeItem === "home"}
              onClick={() => handleNavClick("home", "/dashboard")}
            />
            <NavButton
              href={"/cloud-platforms"}
              name={"Cloud Platforms"}
              icon={Cloud}
              isExpanded={isExpanded}
              isActive={activeItem === "cloud-platforms"}
              onClick={() => handleNavClick("cloud-platforms", "/cloud-platforms")}
            />
            <NavButton
              href={"/scans"}
              name={"Scans"}
              icon={FileSearch}
              isExpanded={isExpanded}
              isActive={activeItem === "scans"}
              onClick={() => handleNavClick("scans", "/scans")}
            />
            <NavButton
              href={"/evidence-scanner"}
              name={"Evidence"}
              icon={ShieldCheck}
              isExpanded={isExpanded}
              isActive={activeItem === "tasks"}
              onClick={() => handleNavClick("tasks", "/evidence-scanner")}
            />
          </ul>
          
          {/* Settings section at bottom */}
          <ul className="nav-settings">
            <NavButton
              href={"/settings"}
              name={"Settings"}
              icon={Settings}
              isExpanded={isExpanded}
              isActive={activeItem === "settings"}
              onClick={() => handleNavClick("settings", "/settings")}
            />
            <NavButton
              href={"/account"}
              name={"Account"}
              icon={User}
              isExpanded={isExpanded}
              isActive={activeItem === "account"}
              onClick={() => handleNavClick("account", "/account")}
            />
          </ul>
        </div>
      </nav>

      {/* Show sidebar button when hidden on mobile/tablet */}
      {isHidden && isMobile && (
        <button className="show-sidebar-button" onClick={() => setIsHidden(false)} aria-label="Show sidebar">
          <Menu size={22} />
        </button>
      )}
    </>
  );
};

export default Sidebar;
