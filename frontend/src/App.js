//Content to be called from this script, which is rendered by index.js
//Create components in the components folder and import them to this script

import logo from './logo.svg';
import './App.css';
import Sidebar from './components/Sidebar'

function App() {
  return (
    <div className="App">
      
       {/* Note: This sidebar should eventually sit under a broader frame component instead of independently*/}
      <Sidebar />

       {/* The below is a stock React landing page. To be removed as soon as we have components for main content. Useful in the meantime for testing components individually.*/}      
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
         

        <p>
          This splash screen is to be replaced with new components as they are built. Useful in the meantime for testing individual components.  
        </p>
        <p>
          Edit <code>src/App.js</code> and save to view changes. New components are to be created in src/components/ folder. 
        </p>
        <p>
          AutoAudit webapp - Ready for editing!
        </p>
      </header>

    </div>
  );
}

export default App;
