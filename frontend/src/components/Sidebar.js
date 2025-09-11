//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 27 August 2025
//To do: 
// -collapsibility 
// -scale width based on screen
// -update styling once styling guide finalised

import React, { useState } from "react";

//Main content
const Sidebar = () => {
    return (
      <nav style={{...sidebarStyle, width: '250px' }}>
        <div style={sidebarContentStyle}>

            {/* Logo and title */}
          <div style={logoStyle}>
            <h2>AutoAudit</h2>
            {/* Logo image to go here once finalised */}
          </div>
          
            {/* Placeholder navigation options, exact options to be updated as we progress */}
          <ul style={navLinksStyle}>
            <li style={navItemStyle}>
              <a 
                href="/" 
                style={linkStyle}
              >
                Home
              </a>
            </li>

            <li style={navItemStyle}>
              <a 
                href="/complianceview" 
                style={linkStyle}
              >
                Compliance Overview
              </a>
            </li>

            <li style={navItemStyle}>
              <a 
                href="/settings" 
                style={linkStyle}
              >
                Settings
              </a>
            </li>

            <li style={navItemStyle}>
              <a 
                href="/userAccount" 
                style={linkStyle}
              >
                User Profile
              </a>
            </li>

          </ul>
        </div>
      </nav>
    );
};

//Styles
//These are placeholders only and will be replaced with references to a unified styleset once available

//style for sidebar background element
const sidebarStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  height: '100vh',
  backgroundColor: '#485a8c',
  overflowX: 'hidden',
  zIndex: 1000, 
  boxShadow: '4px 0 10px rgba(0,0,0,0.1)'
};

//styles for content within the sidebar frame
const sidebarContentStyle = {
  padding: '60px 20px 20px 20px',
  width: '80%',
  textAlign: 'center',
};

const logoStyle = {
  color: 'white',
  textAlign: 'center',
  marginBottom: '30px',
  borderBottom: '1px solid #34495e',
  paddingBottom: '20px'
};

const navLinksStyle = {
  listStyle: 'none',
  margin: 0,
  padding: 0,
  textAlign: 'center'
};

const navItemStyle = {
  marginBottom: '5px',
  borderRadius: '2%',
  backgroundColor: '#374f91',
};

const linkStyle = {
  display: 'block',
  color: 'white',
  textDecoration: 'none',
  padding: '15px 20px',
  fontSize: '16px',
  //borderRadius: '4px',
  margin: '5px 0',
  textAlign: 'center'
};


export default Sidebar;