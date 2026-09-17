import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { TrustScoreBadge } from './TrustScoreBadge';
import { Badge } from './Badge';
import { VynkLogo } from './VynkLogo';

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

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
        </nav>

        {/* Right Section: Auth State */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {isAuthenticated && user ? (
            <>
              <Link to="/profile" className="btn btn-ghost btn-sm" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-primary)' }} title="View & Edit Professional Profile">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.full_name} style={{ width: 20, height: 20, borderRadius: '50%', objectFit: 'cover' }} />
                ) : (
                  <span style={{ fontSize: 13 }}>👤</span>
                )}
                <span>My Profile</span>
              </Link>

              <Link to="/dashboard" style={{ textDecoration: 'none' }}>
                <Badge variant={user.role === 'sponsor' ? 'emerald' : 'cyan'}>
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
