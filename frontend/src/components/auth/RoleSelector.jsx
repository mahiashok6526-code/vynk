import React from 'react';

export function RoleSelector({ selectedRole, onSelectRole }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginBottom: 24 }}>
      {/* Entrepreneur Card */}
      <div
        onClick={() => onSelectRole('entrepreneur')}
        style={{
          cursor: 'pointer',
          padding: '20px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: selectedRole === 'entrepreneur' ? 'rgba(6, 182, 212, 0.08)' : 'rgba(18, 25, 39, 0.6)',
          border: selectedRole === 'entrepreneur' ? '2px solid var(--brand-cyan)' : '1px solid var(--border-subtle)',
          boxShadow: selectedRole === 'entrepreneur' ? '0 0 20px rgba(6, 182, 212, 0.2)' : 'none',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(6, 182, 212, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--brand-cyan)',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v8" />
              <path d="m4.93 10.93 1.41 1.41" />
              <path d="M2 18h2" />
              <path d="M20 18h2" />
              <path d="m19.07 10.93-1.41 1.41" />
              <path d="M22 22H2" />
              <path d="m16 6-4 4-4-4" />
              <path d="M16 18a4 4 0 0 0-8 0" />
            </svg>
          </div>
          {selectedRole === 'entrepreneur' && (
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Selected
            </span>
          )}
        </div>
        <h4 style={{ fontSize: 16, marginBottom: 6, color: 'var(--text-primary)' }}>
          Entrepreneur / Idea Owner
        </h4>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
          I have a startup idea, innovation, or early-stage venture and seek sponsorship, capital, or strategic resources.
        </p>
      </div>

      {/* Sponsor Card */}
      <div
        onClick={() => onSelectRole('sponsor')}
        style={{
          cursor: 'pointer',
          padding: '20px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: selectedRole === 'sponsor' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(18, 25, 39, 0.6)',
          border: selectedRole === 'sponsor' ? '2px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
          boxShadow: selectedRole === 'sponsor' ? '0 0 20px rgba(16, 185, 129, 0.2)' : 'none',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--brand-emerald)',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect width="20" height="14" x="2" y="5" rx="2" />
              <line x1="2" x2="22" y1="10" y2="10" />
            </svg>
          </div>
          {selectedRole === 'sponsor' && (
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-emerald)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Selected
            </span>
          )}
        </div>
        <h4 style={{ fontSize: 16, marginBottom: 6, color: 'var(--text-primary)' }}>
          Sponsor / Backer / Fund
        </h4>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
          I represent a fund, company, angel, or grant provider seeking high-potential projects to sponsor and support.
        </p>
      </div>
    </div>
  );
}
