import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { TrustScoreBadge } from './TrustScoreBadge';
import { Badge } from './Badge';

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
        {/* Brand Logo & Tagline */}
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            textDecoration: 'none',
          }}
        >
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(16, 185, 129, 0.15) 100%)',
              border: '1px solid var(--border-glow)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow-cyan)',
            }}
          >
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
              <path
                d="M7 9L16 23L25 9"
                stroke="url(#vynk-grad)"
                strokeWidth="3.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="16" cy="23" r="2.5" fill="#10B981" />
              <circle cx="7" cy="9" r="1.5" fill="#06B6D4" />
              <circle cx="25" cy="9" r="1.5" fill="#6366F1" />
              <defs>
                <linearGradient id="vynk-grad" x1="7" y1="9" x2="25" y2="23" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#06B6D4" />
                  <stop offset="0.5" stopColor="#10B981" />
                  <stop offset="1" stopColor="#6366F1" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 22,
                fontWeight: 800,
                letterSpacing: '-0.03em',
                color: 'var(--text-primary)',
              }}
            >
              Vynk
            </span>
            <span
              style={{
                display: 'block',
                fontSize: 10,
                color: 'var(--text-muted)',
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                marginTop: -4,
                fontWeight: 600,
              }}
            >
              Ideas Meet Opportunities
            </span>
          </div>
        </Link>

        {/* Center / Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <Link to="/" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Overview
          </Link>
          <a href="#how-it-works" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            How It Works
          </a>
          <a href="#trust-architecture" style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>
            Trust Architecture
          </a>
        </nav>

        {/* Right Section: Auth State */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {isAuthenticated && user ? (
            <>
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
