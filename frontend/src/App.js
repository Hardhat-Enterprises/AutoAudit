import React, { useState } from 'react';
import Dashboard from './Dashboard';
import Sidebar from './components/Sidebar';

function App() {

  //We establish sidebar width at this parent level so it is visible to subpages and can exist on top of everything else.
  const [sidebarWidth, setSidebarWidth] = useState(220);

  //The navbar is placed at this higher level (instead of the dashboard.js) so that we can implement page switching at this level, replacing the Dashboard component with our current page, and the navbar will remain. 
  //We pass the sidebar width to the dashboard component. A better solution would be to have a page container element, that contains the dashboard within, and we pass the width to that instead. Not yet implemented. 
  return (
    <div className="App">
      <Sidebar onWidthChange={setSidebarWidth}/>
      <Dashboard sidebarWidth={sidebarWidth}/>
    </div>
  );
}
export default App;