import React, { useState, useEffect, JSX } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Dashboard Components
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Evidence from './pages/Evidence';
import SettingsPage from './pages/SettingsPage';
import AccountPage from './pages/AccountPage';
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
import ContactAdminPage from './pages/Admin/ContactAdminPage';
import GoogleCallbackPage from './pages/Auth/GoogleCallbackPage';

// Auth Context
import { useAuth } from './context/AuthContext';
import { register as apiRegister } from './api/client';

// Styles
import './styles/global.css';

interface RouteWrapperProps {
  children: React.ReactNode;
}

interface DashboardChildProps {
  sidebarWidth?: number;
  isDarkMode?: boolean;
  onThemeToggle?: () => void;
}

interface DashboardLayoutProps {
  children: React.ReactElement<DashboardChildProps>;
  sidebarWidth: number;
  isDarkMode: boolean;
  onThemeToggle: () => void;
  onSidebarWidthChange: (width: number) => void;
}

interface SignUpData {
  email: string;
  password: string;
}

// Protected Route Component
const ProtectedRoute: React.FC<RouteWrapperProps> = ({ children }) => {
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

  return isAuthenticated ? <>{children}</> : null;
};

// Admin-only Route Component
const AdminRoute: React.FC<RouteWrapperProps> = ({ children }) => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, user } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if ((user as { role?: string } | null | undefined)?.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [isAuthenticated, isLoading, navigate, user]);

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return isAuthenticated && (user as { role?: string } | null | undefined)?.role === 'admin' ? <>{children}</> : null;
};

// Dashboard Layout Component (with sidebar)
const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  sidebarWidth,
  isDarkMode,
  onThemeToggle,
  onSidebarWidthChange,
}) => {
  return (
    <>
      <Sidebar onWidthChange={onSidebarWidthChange} isDarkMode={isDarkMode} />
      {React.cloneElement(children, { sidebarWidth, isDarkMode, onThemeToggle })}
    </>
  );
};

function App(): JSX.Element {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Dashboard state
  const getInitialSidebarWidth = (): number => {
    if (typeof window === 'undefined') return 220;
    try {
      const stored = window.localStorage.getItem('sidebarExpanded');
      if (stored === null) return 220;
      return stored === 'true' ? 220 : 80;
    } catch {
      return 220;
    }
  };

  const [sidebarWidth, setSidebarWidth] = useState<number>(getInitialSidebarWidth);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);

  // Theme management
  useEffect(() => {
    const theme = localStorage.getItem('theme') ?? 'dark';
    const dark = theme === 'dark';
    setIsDarkMode(dark);

    const root = document.documentElement;
    if (dark) {
      root.classList.remove('light');
    } else {
      root.classList.add('light');
    }
  }, []);

  // Scroll restoration:
  // - On route changes without hash, go to top.
  // - Keep hash-based anchor behavior (e.g. /#features) intact.
  useEffect(() => {
    if (location.hash) return;
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, [location.pathname, location.hash]);

  // Authentication handlers
  const handleUserLogin = async (email: string, password: string, remember: boolean = true): Promise<void> => {
    await auth.login(email, password, remember);
    navigate('/dashboard');
  };

  const handleUserLogout = (): void => {
    auth.logout();
    navigate('/');
  };

  const handleSignUp = async (signUpData: SignUpData): Promise<void> => {
    const email = signUpData.email;
    const password = signUpData.password;

    if (!email || !password) {
      throw new Error('Email and password are required');
    }

    await apiRegister(email, password);
    await auth.login(email, password, true);
    navigate('/dashboard');
  };

  const handleThemeToggle = (): void => {
    const newThemeIsDark = !isDarkMode;
    setIsDarkMode(newThemeIsDark);
    localStorage.setItem('theme', newThemeIsDark ? 'dark' : 'light');

    const root = document.documentElement;
    if (newThemeIsDark) {
      root.classList.remove('light');
    } else {
      root.classList.add('light');
    }
  };

  const handleSidebarWidthChange = (width: number): void => {
    setSidebarWidth(width);
  };

  return (
    <div className="App">
      <Routes>
        {/* Public Routes */}
        <Route
          path="/"
          element={<LandingPage onSignInClick={() => navigate('/login')} />}
        />

        <Route
          path="/about"
          element={
            <AboutUs onSignInClick={() => navigate('/login')} />
          }
        />

        <Route
          path="/contact"
          element={<ContactPage onSignIn={() => navigate('/login')} />}
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

        <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />

        <Route
          path="/signup"
          element={
            <SignUpPage
              onSignUp={handleSignUp}
              onBackToLogin={() => navigate('/login')}
            />
          }
        />

        <Route
          path="/admin/contact-submissions"
          element={
            <AdminRoute>
              <ContactAdminPage />
            </AdminRoute>
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
                <Dashboard isDarkMode={isDarkMode} onThemeToggle={handleThemeToggle} />
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
          path="/settings"
          element={
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <SettingsPage />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <DashboardLayout
                sidebarWidth={sidebarWidth}
                isDarkMode={isDarkMode}
                onThemeToggle={handleThemeToggle}
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <AccountPage />
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

        <Route path="/styleguide" element={<StyleGuide />} />

        {/* Fallback route */}
        <Route
          path="*"
          element={
            <LandingPage
              onSignInClick={() => navigate('/login')}
            />
          }
        />
      </Routes>
    </div>
  );
}

export default App;