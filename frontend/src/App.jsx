import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { EntrepreneurDashboard } from './pages/dashboards/EntrepreneurDashboard';
import { SponsorDashboard } from './pages/dashboards/SponsorDashboard';
import { AdminDashboard } from './pages/dashboards/AdminDashboard';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';

// Central dispatcher for /dashboard that routes directly based on active role
function DashboardDispatcher() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === 'sponsor') {
    return <Navigate to="/dashboard/sponsor" replace />;
  }
  if (user.role === 'admin') {
    return <Navigate to="/dashboard/admin" replace />;
  }
  return <Navigate to="/dashboard/entrepreneur" replace />;
}

export function App() {
  return (
    <AuthProvider>
      <Router>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flex: 1 }}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/p/:identifier" element={<ProfilePage />} />
              <Route path="/profile/:identifier" element={<ProfilePage />} />

              {/* Protected Profile Route */}
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Protected Dashboard Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardDispatcher />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/entrepreneur"
                element={
                  <ProtectedRoute allowedRoles={['entrepreneur']}>
                    <EntrepreneurDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/sponsor"
                element={
                  <ProtectedRoute allowedRoles={['sponsor']}>
                    <SponsorDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/admin"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Fallback 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
