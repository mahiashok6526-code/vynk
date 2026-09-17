import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { TrustScoreBadge } from './TrustScoreBadge';
import { Badge } from './Badge';
import { VynkLogo } from './VynkLogo';
import { notificationService } from '../../services/notificationService';

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCounts, setUnreadCounts] = useState({ unread_messages: 0, unread_notifications: 0 });

  useEffect(() => {
    if (!isAuthenticated) return;

    let isMounted = true;
    const fetchCounts = async () => {
      try {
        const data = await notificationService.getUnreadSummary();
        if (isMounted && data) {
          setUnreadCounts({
            unread_messages: data.unread_messages || 0,
            unread_notifications: data.unread_notifications || 0,
          });
        }
      } catch (err) {
        // Silently catch background polling errors
      }
    };

    fetchCounts();
    // Approved polling interval: navbar unread counts ~20 seconds
    const interval = setInterval(fetchCounts, 20000);

    const handleRefresh = () => fetchCounts();
    window.addEventListener('vynk:refresh-unread', handleRefresh);

    return () => {
      isMounted = false;
      clearInterval(interval);
      window.removeEventListener('vynk:refresh-unread', handleRefresh);
    };
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backgroundColor: 'rgba(7, 9, 14, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-subtle)',
        height: 'var(--header-height)',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
        }}
      >
        {/* Official Vynk Brand Logo */}
        <VynkLogo variant="full" size={38} withLink />

        {/* Center / Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <Link to="/" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Overview
          </Link>
          <Link to="/projects" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Discover Projects
          </Link>
          <Link to="/sponsors" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Find Sponsors
          </Link>
          <a href="/#how-it-works" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            How It Works
          </a>
          <a href="/#trust-architecture" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Trust Architecture
          </a>
          {isAuthenticated && (
            <Link to="/profile" style={{ color: 'var(--brand-cyan)', fontSize: 14, fontWeight: 600 }}>
              My Profile
            </Link>
          )}
          {isAuthenticated && user?.role === 'admin' && (
            <Link to="/admin" style={{ color: '#818CF8', fontSize: 14, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
              <span>🛡️</span> Admin Console
            </Link>
          )}
        </nav>

        {/* Right Section: Auth State */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {isAuthenticated && user ? (
            <>
              {/* Messages Navigation Link with Badge */}
              <Link
                to="/messages"
                className="btn btn-ghost btn-sm"
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  color: unreadCounts.unread_messages > 0 ? 'var(--brand-cyan)' : 'var(--text-secondary)',
                  padding: '6px 10px',
                }}
                title="Direct Messages"
                id="nav-messages-link"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span style={{ fontSize: 13, fontWeight: 500 }}>Messages</span>
                {unreadCounts.unread_messages > 0 && (
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minWidth: 18,
                      height: 18,
                      padding: '0 5px',
                      borderRadius: 999,
                      backgroundColor: 'var(--brand-cyan)',
                      color: 'var(--text-inverse)',
                      fontSize: 11,
                      fontWeight: 700,
                      lineHeight: 1,
                      boxShadow: '0 0 8px var(--brand-cyan-glow)',
                    }}
                    id="nav-unread-messages-badge"
                  >
                    {unreadCounts.unread_messages > 99 ? '99+' : unreadCounts.unread_messages}
                  </span>
                )}
              </Link>

              {/* Notification Bell Button with Badge */}
              <Link
                to="/notifications"
                className="btn btn-ghost btn-sm"
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 36,
                  height: 36,
                  padding: 0,
                  borderRadius: 'var(--radius-md)',
                  color: unreadCounts.unread_notifications > 0 ? 'var(--brand-amber)' : 'var(--text-secondary)',
                }}
                title="Notification Center"
                id="nav-notifications-link"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                {unreadCounts.unread_notifications > 0 && (
                  <span
                    style={{
                      position: 'absolute',
                      top: 4,
                      right: 4,
                      minWidth: 16,
                      height: 16,
                      padding: '0 4px',
                      borderRadius: 999,
                      backgroundColor: 'var(--brand-amber)',
                      color: '#000',
                      fontSize: 10,
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      lineHeight: 1,
                      boxShadow: '0 0 8px rgba(245, 158, 11, 0.4)',
                    }}
                    id="nav-unread-notifications-badge"
                  >
                    {unreadCounts.unread_notifications > 99 ? '99+' : unreadCounts.unread_notifications}
                  </span>
                )}
              </Link>

              <Link to="/dashboard" style={{ textDecoration: 'none' }}>
                <Badge variant={user.role === 'sponsor' ? 'emerald' : user.role === 'admin' ? 'indigo' : 'cyan'}>
                  {user.role}
                </Badge>
              </Link>

              <TrustScoreBadge
                score={user.trust_score?.score ?? 50}
                size="sm"
                showLabel={false}
              />

              <Link
                to="/dashboard"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  textDecoration: 'none',
                  color: 'var(--text-primary)',
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                <span>{user.full_name}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="btn btn-ghost btn-sm"
                style={{ color: 'var(--text-muted)' }}
                title="Sign out of Vynk"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm">
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
