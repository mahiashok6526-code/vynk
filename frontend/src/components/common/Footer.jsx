import React from 'react';
import { Link } from 'react-router-dom';
import { VynkLogo } from './VynkLogo';

export function Footer() {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-secondary)',
        padding: '50px 0 30px',
        marginTop: 80,
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 40,
            marginBottom: 40,
          }}
        >
          {/* Brand Info */}
          <div>
            <div style={{ marginBottom: 14 }}>
              <VynkLogo variant="full" size={32} withLink />
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: 280 }}>
              The modern professional networking and sponsorship platform connecting idea creators with serious sponsors through verifiable trust.
            </p>
            <div style={{ marginTop: 16, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10B981' }} />
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Phase 1 Foundation Active</span>
            </div>
          </div>

          {/* Workflow */}
          <div>
            <h4 style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Core Lifecycle
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
              <li>1. Discover Opportunities</li>
              <li>2. AI Compatibility Match</li>
              <li>3. Connect & Inquire</li>
              <li>4. Structured Commitment</li>
              <li>5. Track Lifecycle</li>
              <li>6. Verifiable Trust Score</li>
            </ul>
          </div>

          {/* Platform */}
          <div>
            <h4 style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Roles & Portals
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 }}>
              <li>
                <Link to="/register" style={{ color: 'var(--text-secondary)' }}>For Entrepreneurs</Link>
              </li>
              <li>
                <Link to="/register" style={{ color: 'var(--text-secondary)' }}>For Sponsors & Angels</Link>
              </li>
              <li>
                <Link to="/login" style={{ color: 'var(--text-secondary)' }}>Sign In to Portal</Link>
              </li>
              <li>
                <a href="/api/v1/docs" target="_blank" rel="noreferrer" style={{ color: 'var(--brand-cyan)' }}>
                  Interactive API Docs ↗
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: 24,
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 16,
            fontSize: 12,
            color: 'var(--text-muted)',
          }}
        >
          <div>
            © {new Date().getFullYear()} Vynk Technologies. Ideas Meet Opportunities. All rights reserved.
          </div>
          <div>
            FastAPI · PostgreSQL-Ready · React · Vite · Clean Pluggable AI Service Layer
          </div>
        </div>
      </div>
    </footer>
  );
}
