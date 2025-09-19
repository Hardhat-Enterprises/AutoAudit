import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/tokens.css';
import './index.css';
import App from './App';
import { BrowserRouter as Router } from 'react-router-dom';

//To run: cd into /frontend/
//command: npm start

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>
);
