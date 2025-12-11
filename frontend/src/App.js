import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Dashboard Components
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Evidence from './pages/Evidence';
import StyleGuide from './pages/StyleGuide';
import ConnectionsPage from './pages/Connections/ConnectionsPage';
import ScansPage from './pages/Scans/ScansPage';
import ScanDetailPage from './pages/Scans/ScanDetailPage';

// Authentication & Landing Components
import LandingPage from './pages/Landing/LandingPage';
import AboutUs from './pages/Landing/AboutUs';
import ContactPage from './pages/Contact/ContactPage';
import LoginPage from './pages/Auth/LoginPage';
import SignUpPage from './pages/Auth/SignUpPage';

// Auth Context
import { useAuth } from './context/AuthContext';

// Styles
import './styles/global.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return isAuthenticated ? children : null;
};

// Dashboard Layout Component (with sidebar)
const DashboardLayout = ({ children, sidebarWidth, isDarkMode, onThemeToggle, onSidebarWidthChange }) => {
  return (
    <>
      <Sidebar onWidthChange={onSidebarWidthChange} isDarkMode={isDarkMode} />
      {React.cloneElement(children, { sidebarWidth, isDarkMode, onThemeToggle })}
    </>
  );
};

function App() {
  const auth = useAuth();

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
  const handleUserLogin = async (email, password) => {
    await auth.login(email, password);
    navigate('/dashboard');
  };

  const handleUserLogout = () => {
    auth.logout();
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
  const isDashboardRoute = ['/dashboard', '/evidence-scanner', '/styleguide', '/cloud-platforms', '/scans'].includes(location.pathname) || location.pathname.startsWith('/scans/');

  return (
    <div className="App">
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/" 
          element={
            <LandingPage 
              onSignInClick={() => navigate('/login')}
            />
          } 
        />
        
        <Route 
          path="/about" 
          element={
            <AboutUs 
              onBack={() => navigate('/')} 
              onSignInClick={() => navigate('/login')}
            />
          } 
        />
        
        <Route
          path="/contact"
          element={
            <ContactPage
              onSignIn={() => navigate('/login')}
            />
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
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
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
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <Evidence />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/cloud-platforms"
          element={
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <ConnectionsPage isDarkMode={isDarkMode} />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/scans"
          element={
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <ScansPage isDarkMode={isDarkMode} />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/scans/:scanId"
          element={
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <ScanDetailPage isDarkMode={isDarkMode} />
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
              onContactClick={() => navigate('/contact')}
            />
          } 
        />
      </Routes>
    </div>
  );
}

export default App;
