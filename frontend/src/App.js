import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Dashboard Components
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Evidence from './pages/Evidence';
import StyleGuide from './pages/StyleGuide';

// Authentication & Landing Components
import LandingPage from './pages/Landing/LandingPage';
import AboutUs from './pages/Landing/AboutUs';
import LoginPage from './pages/Auth/LoginPage';
import SignUpPage from './pages/Auth/SignUpPage';

// Styles
import './styles/global.css';

// Protected Route Component
const ProtectedRoute = ({ children, isAuthenticated }) => {
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return isAuthenticated ? children : null;
};

// Dashboard Layout Component (with sidebar)
const DashboardLayout = ({ children, sidebarWidth, isDarkMode, onThemeToggle }) => {
  return (
    <>
      <Sidebar onWidthChange={() => {}} isDarkMode={isDarkMode} />
      {React.cloneElement(children, { sidebarWidth, isDarkMode, onThemeToggle })}
    </>
  );
};

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(
  process.env.NODE_ENV === 'development' ? true : false
  );
  
  // Dashboard state
  const [sidebarWidth, setSidebarWidth] = useState(220);
  const [isDarkMode, setIsDarkMode] = useState(true);
  
  const location = useLocation();
  const navigate = useNavigate();

  // Theme management
  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.remove('light');
    } else {
      root.classList.add('light');
    }
  }, [isDarkMode]);

  // Authentication handlers
  const handleUserLogin = () => {
    setIsAuthenticated(true);
    navigate('/dashboard');
  };

  const handleUserLogout = () => {
    setIsAuthenticated(false);
    navigate('/');
  };

  const handleSignUp = (signUpData) => {
    console.log("Sign up data:", signUpData);
    navigate('/login');
  };

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleSidebarWidthChange = (width) => {
    setSidebarWidth(width);
  };

  // Check if current route should show sidebar
  const isDashboardRoute = ['/dashboard', '/evidence-scanner', '/styleguide'].includes(location.pathname);

  return (
    <div className="App">
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/" 
          element={
            <LandingPage 
              onSignInClick={() => navigate('/login')}
              onAboutClick={() => navigate('/about')}
            />
          } 
        />
        
        <Route 
          path="/about" 
          element={
            <AboutUs onBack={() => navigate('/')} />
          } 
        />
        
        <Route 
          path="/login" 
          element={
            <LoginPage 
              onLogin={handleUserLogin}
              onSignUpClick={() => navigate('/signup')}
            />
          } 
        />
        
        <Route 
          path="/signup" 
          element={
            <SignUpPage 
              onSignUp={handleSignUp}
              onBackToLogin={() => navigate('/login')}
            />
          } 
        />

        {/* Protected Dashboard Routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <DashboardLayout 
                sidebarWidth={sidebarWidth} 
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
              >
                <Dashboard 
                  onThemeToggle={handleThemeToggle}
                />
              </DashboardLayout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/evidence-scanner" 
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <DashboardLayout 
                sidebarWidth={sidebarWidth} 
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
              >
                <Evidence />
              </DashboardLayout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/styleguide" 
          element={<StyleGuide />} 
        />

        {/* Fallback route */}
        <Route 
          path="*" 
          element={
            <LandingPage 
              onSignInClick={() => navigate('/login')}
              onAboutClick={() => navigate('/about')}
            />
          } 
        />
      </Routes>
    </div>
  );
}

export default App;