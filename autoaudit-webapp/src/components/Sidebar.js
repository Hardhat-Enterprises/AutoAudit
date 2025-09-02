//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 2 September 2025
//To do:
// -collapsibility [done]
// -scale width based on screen
// -update styling once styling guide finalised
import React, { useState } from "react";
import './Sidebar.css';

//Main content
const Sidebar = () => {
    const [isExpanded, setIsExpanded] = useState(true); // State to track if sidebar is expanded (starts open, can be collapsed)
    const toggleSidebar = () => {
        setIsExpanded(!isExpanded);
    };
 
 
  return (          
      <nav className="sidebar" style={{'--sidebar-width': isExpanded ? '250px' : '0px'}}>
        <div className="sidebar-content">
           
            <button className="toggle-button" onClick={toggleSidebar}>
                {isExpanded ? '←' : '☰'} {/* Arrow when open, hamburger when closed */}
            </button>
            {/* Logo and title */}
          <div className="logo">
            <h2>AutoAudit</h2>
            {/* Logo image to go here once finalised */}
          </div>
         
            {/* Placeholder navigation options, exact options to be updated as we progress */}
          <ul className="nav-links">
            <li className="nav-item">
              <a
                href="/"
                className="nav-link"
              >
                Home
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/complianceview"
                className="nav-link"
              >
                Compliance Overview
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/recomendations"
                className="nav-link"
              >
                Recomended Actions
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/reports"
                className="nav-link"
              >
                Reports
              </a>
            </li>
           
          </ul>
          {/* Placeholder navigation options for bottom of screen*/}
          <ul className="nav-settings">
            <li className="nav-item">
              <a
                href="/settings"
                className="nav-link"
              >
                Settings
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/userAccount"
                className="nav-link"
              >
                User Profile
              </a>
            </li>
          </ul>
        </div>
      </nav>
    );
};

export default Sidebar;