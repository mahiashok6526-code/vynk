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
import { AdminLayout } from './components/admin/AdminLayout';
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { AdminUsersPage } from './pages/admin/AdminUsersPage';
import { AdminProjectsPage } from './pages/admin/AdminProjectsPage';
import { AdminReportsPage } from './pages/admin/AdminReportsPage';
import { AdminDisputesPage } from './pages/admin/AdminDisputesPage';
import { AdminAuditLogsPage } from './pages/admin/AdminAuditLogsPage';
import { ProfilePage } from './pages/ProfilePage';
import { ProjectsDiscoveryPage } from './pages/projects/ProjectsDiscoveryPage';
import { SponsorsDiscoveryPage } from './pages/sponsors/SponsorsDiscoveryPage';
import { ProjectCreatePage } from './pages/projects/ProjectCreatePage';
import { ProjectDetailPage } from './pages/projects/ProjectDetailPage';
import { ProjectEditPage } from './pages/projects/ProjectEditPage';
import { CommitmentDetailPage } from './pages/commitments/CommitmentDetailPage';
import { MessagesPage } from './pages/messages/MessagesPage';
import { NotificationsPage } from './pages/notifications/NotificationsPage';
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
    return <Navigate to="/admin" replace />;
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

              {/* Project & Sponsor Showcase Routes */}
              <Route path="/projects" element={<ProjectsDiscoveryPage />} />
              <Route path="/sponsors" element={<SponsorsDiscoveryPage />} />
              <Route
                path="/projects/new"
                element={
                  <ProtectedRoute allowedRoles={['entrepreneur']}>
                    <ProjectCreatePage />
                  </ProtectedRoute>
                }
              />
              <Route path="/projects/:id" element={<ProjectDetailPage />} />
              <Route
                path="/projects/:id/edit"
                element={
                  <ProtectedRoute allowedRoles={['entrepreneur']}>
                    <ProjectEditPage />
                  </ProtectedRoute>
                }
              />

              {/* Protected Profile Route */}
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Sponsorship Commitment Detail Route */}
              <Route
                path="/commitments/:id"
                element={
                  <ProtectedRoute>
                    <CommitmentDetailPage />
                  </ProtectedRoute>
                }
              />

              {/* Secure Messaging Route */}
              <Route
                path="/messages"
                element={
                  <ProtectedRoute>
                    <MessagesPage />
                  </ProtectedRoute>
                }
              />

              {/* Notification Center Route */}
              <Route
                path="/notifications"
                element={
                  <ProtectedRoute>
                    <NotificationsPage />
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
              {/* Phase 9 Admin & Moderation Routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<AdminDashboardPage />} />
                <Route path="users" element={<AdminUsersPage />} />
                <Route path="projects" element={<AdminProjectsPage />} />
                <Route path="reports" element={<AdminReportsPage />} />
                <Route path="disputes" element={<AdminDisputesPage />} />
                <Route path="audit-logs" element={<AdminAuditLogsPage />} />
              </Route>
              {/* Backwards-compatible /dashboard/admin redirect */}
              <Route
                path="/dashboard/admin"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <Navigate to="/admin" replace />
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
