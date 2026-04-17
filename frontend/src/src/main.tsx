import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

/* Import global Tailwind CSS */
import './styles/global.css';

/* Render the app */
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);