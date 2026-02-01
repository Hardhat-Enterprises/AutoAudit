import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Fonts (load once at app startup to reduce layout shifts)
import '@fontsource/league-spartan/400.css';
import '@fontsource/league-spartan/600.css';
import '@fontsource/league-spartan/700.css';


// Tailwind + tokens + base (includes tokens.css & components.css)
import './styles/global.css';

// Legacy app styles (keeps current look intact)
import './index.css';

import App from './App.jsx';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Router>
  </React.StrictMode>
);