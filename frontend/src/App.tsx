import React, { useState, useEffect, JSX } from "react";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";

// Dashboard Components
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Evidence from "./pages/Evidence";
import SettingsPage from "./pages/SettingsPage";
import AccountPage from "./pages/AccountPage";
import StyleGuide from "./pages/StyleGuide";
import ConnectionsPage from "./pages/Connections/ConnectionsPage";
import ScansPage from "./pages/Scans/ScansPage";
import ScanDetailPage from "./pages/Scans/ScanDetailPage";

// Authentication & Landing Components
import LandingPage from "./pages/Landing/LandingPage";
import AboutUs from "./pages/Landing/AboutUs";
import ContactPage from "./pages/Contact/ContactPage";
import LoginPage from "./pages/Auth/LoginPage";
import SignUpPage from "./pages/Auth/SignUpPage";
import ContactAdminPage from "./pages/Admin/ContactAdminPage";
import GoogleCallbackPage from "./pages/Auth/GoogleCallbackPage";

// Auth Context
import { useAuth } from "./context/AuthContext";
import { register as apiRegister } from "./api/client";

// Styles
import "./index.css";

type RouteWrapperProps = {
  children: React.ReactNode;
};

type DashboardChildProps = {
  sidebarWidth?: number;
  isDarkMode?: boolean;
};

type DashboardLayoutProps = {
  children: React.ReactElement<DashboardChildProps>;
  sidebarWidth: number;
  isDarkMode: boolean;
  onSidebarWidthChange: (width: number) => void;
};

type SignUpData = {
  firstName: string;
  lastName: string;
  email: string;
  organizationName: string;
  password: string;
  confirmPassword: string;
  agreeTerms: boolean;
};

const LoadingScreen = (): JSX.Element => (
  <div className="flex h-screen items-center justify-center bg-slate-900">
    <div className="text-center">
      <div className="animate-spin">
        <svg
          className="h-8 w-8 text-blue-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      <p className="mt-4 text-slate-400">Loading...</p>
    </div>
  </div>
);

// Protected Route Component
const ProtectedRoute: React.FC<RouteWrapperProps> = ({ children }) => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    return <LoadingScreen />;
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
      navigate("/login");
      return;
    }

    if ((user as { role?: string } | null | undefined)?.role !== "admin") {
      navigate("/dashboard");
    }
  }, [isAuthenticated, isLoading, navigate, user]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return isAuthenticated &&
    (user as { role?: string } | null | undefined)?.role === "admin" ? (
    <>{children}</>
  ) : null;
};

// Dashboard Layout Component with sidebar
const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  sidebarWidth,
  isDarkMode,
  onSidebarWidthChange,
}) => {
  return (
    <>
      <Sidebar onWidthChange={onSidebarWidthChange} isDarkMode={isDarkMode} />
      {React.cloneElement(children, { sidebarWidth, isDarkMode })}
    </>
  );
};

function App(): JSX.Element {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const showPublicEnhancements = ["/", "/about", "/contact"].includes(
    location.pathname,
  );

  // Dashboard state
  const getInitialSidebarWidth = (): number => {
    if (typeof window === "undefined") return 220;

    try {
      const stored = window.localStorage.getItem("sidebarExpanded");

      if (stored === null) return 220;

      return stored === "true" ? 220 : 80;
    } catch {
      return 220;
    }
  };

  const [sidebarWidth, setSidebarWidth] = useState<number>(
    getInitialSidebarWidth,
  );
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);

  // Theme management
  useEffect(() => {
    const theme = localStorage.getItem("theme") ?? "dark";
    const dark = theme === "dark";

    setIsDarkMode(dark);

    const root = document.documentElement;

    if (dark) {
      root.classList.remove("light");
    } else {
      root.classList.add("light");
    }
  }, []);

  // Scroll restoration
  useEffect(() => {
    if (location.hash) return;

    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [location.pathname, location.hash]);

  // Authentication handlers
  const handleUserLogin = async (
    email: string,
    password: string,
    remember: boolean = true,
  ): Promise<void> => {
    await auth.login(email, password, remember);
    navigate("/dashboard");
  };

  const handleUserLogout = (): void => {
    auth.logout();
    navigate("/");
  };

  const handleSignUp = async (signUpData: SignUpData): Promise<void> => {
    const { firstName, lastName, email, organizationName, password } =
      signUpData;

    if (!firstName || !lastName || !email || !organizationName || !password) {
      throw new Error("All fields are required");
    }

    await apiRegister({
      firstName,
      lastName,
      email,
      organizationName,
      password,
    });

    await auth.login(email, password, true);
    navigate("/dashboard");
  };

  const handleThemeToggle = (): void => {
    const newThemeIsDark = !isDarkMode;

    setIsDarkMode(newThemeIsDark);
    localStorage.setItem("theme", newThemeIsDark ? "dark" : "light");

    const root = document.documentElement;

    if (newThemeIsDark) {
      root.classList.remove("light");
    } else {
      root.classList.add("light");
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
          element={<LandingPage onSignInClick={() => navigate("/login")} />}
        />

        <Route
          path="/about"
          element={<AboutUs onSignInClick={() => navigate("/login")} />}
        />

        <Route
          path="/contact"
          element={<ContactPage onSignIn={() => navigate("/login")} />}
        />

        <Route
          path="/login"
          element={
            <LoginPage
              onLogin={handleUserLogin}
              onSignUpClick={() => navigate("/signup")}
            />
          }
        />

        <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />

        <Route
          path="/signup"
          element={
            <SignUpPage
              onSignUp={handleSignUp}
              onBackToLogin={() => navigate("/login")}
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
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <Dashboard isDarkMode={isDarkMode} />
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
                onSidebarWidthChange={handleSidebarWidthChange}
              >
                <ScanDetailPage isDarkMode={isDarkMode} />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route path="/styleguide" element={<StyleGuide />} />

        {/* Fallback Route */}
        <Route
          path="*"
          element={<LandingPage onSignInClick={() => navigate("/login")} />}
        />
      </Routes>

      {showPublicEnhancements && (
        <>
          <section className="w-full bg-gradient-to-b from-surface-1 to-surface-2 px-6 py-16 text-text-strong">
            <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.1fr_1.9fr] lg:items-center">
              <div>
                <span className="inline-flex rounded-full border border-accent-teal/20 bg-accent-teal/10 px-3 py-2 text-xs font-bold uppercase tracking-wide text-accent-teal">
                  Audit Readiness
                </span>

                <h2 className="mt-4 max-w-2xl text-3xl font-bold leading-tight md:text-4xl">
                  Built to support faster compliance preparation
                </h2>

                <p className="mt-4 max-w-2xl text-sm leading-7 text-text-muted md:text-base">
                  AutoAudit brings evidence review, cloud visibility, and audit
                  tracking into one streamlined workflow, helping teams stay
                  prepared before compliance reviews begin.
                </p>
              </div>

              <div className="grid gap-5 md:grid-cols-3">
                <article className="min-h-40 rounded-2xl border border-text-muted/20 bg-surface-1/60 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <h3 className="text-base font-bold text-text-strong">
                    Evidence Visibility
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Organise and review audit evidence across connected systems.
                  </p>
                </article>

                <article className="min-h-40 rounded-2xl border border-text-muted/20 bg-surface-1/60 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <h3 className="text-base font-bold text-text-strong">
                    Risk Awareness
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Highlight compliance gaps early so teams can respond before
                    audit deadlines.
                  </p>
                </article>

                <article className="min-h-40 rounded-2xl border border-text-muted/20 bg-surface-1/60 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <h3 className="text-base font-bold text-text-strong">
                    Workflow Clarity
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Keep compliance tasks clear, trackable, and easier to manage.
                  </p>
                </article>
              </div>
            </div>
          </section>

          <section className="w-full bg-surface-1 px-6 py-16 text-text-strong">
            <div className="mx-auto max-w-7xl">
              <div className="mb-9 max-w-3xl">
                <span className="inline-flex rounded-full border border-accent-teal/20 bg-accent-teal/10 px-3 py-2 text-xs font-bold uppercase tracking-wide text-accent-teal">
                  Platform Value
                </span>

                <h2 className="mt-4 text-3xl font-bold leading-tight md:text-4xl">
                  Designed for clear, secure, and reliable audit workflows
                </h2>

                <p className="mt-4 text-sm leading-7 text-text-muted md:text-base">
                  The public interface now communicates AutoAudit’s value more
                  clearly by highlighting usability, consistency, compliance
                  focus, and responsive access across different screen sizes.
                </p>
              </div>

              <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
                <article className="rounded-2xl border border-text-muted/20 bg-surface-2/70 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <span className="text-xs font-extrabold uppercase tracking-wide text-accent-teal">
                    01
                  </span>
                  <h3 className="mt-4 text-base font-bold text-text-strong">
                    Clear Navigation
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Supports users in understanding audit-related features with
                    less friction.
                  </p>
                </article>

                <article className="rounded-2xl border border-text-muted/20 bg-surface-2/70 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <span className="text-xs font-extrabold uppercase tracking-wide text-accent-teal">
                    02
                  </span>
                  <h3 className="mt-4 text-base font-bold text-text-strong">
                    Consistent Interface
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Strengthens the visual structure of public-facing product
                    sections.
                  </p>
                </article>

                <article className="rounded-2xl border border-text-muted/20 bg-surface-2/70 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <span className="text-xs font-extrabold uppercase tracking-wide text-accent-teal">
                    03
                  </span>
                  <h3 className="mt-4 text-base font-bold text-text-strong">
                    Compliance Focus
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Highlights evidence, risk, and governance workflows in a
                    professional way.
                  </p>
                </article>

                <article className="rounded-2xl border border-text-muted/20 bg-surface-2/70 p-6 shadow-lg transition hover:-translate-y-1 hover:border-accent-teal/30 hover:shadow-xl">
                  <span className="text-xs font-extrabold uppercase tracking-wide text-accent-teal">
                    04
                  </span>
                  <h3 className="mt-4 text-base font-bold text-text-strong">
                    Responsive Layout
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    Improves the presentation across desktop, tablet, and mobile
                    screens using Tailwind utility classes.
                  </p>
                </article>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;