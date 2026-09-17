import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { VynkLogo } from '../common/VynkLogo';
import { Badge } from '../common/Badge';

export function AdminLayout({ children }) {
  const navItems = [
    { to: '/admin', label: 'Dashboard', icon: '📊', exact: true },
    { to: '/admin/users', label: 'Users & Trust', icon: '👥' },
    { to: '/admin/projects', label: 'Project Moderation', icon: '🚀' },
    { to: '/admin/reports', label: 'Reports', icon: '⚠️' },
    { to: '/admin/disputes', label: 'Disputes', icon: '⚖️' },
    { to: '/admin/audit-logs', label: 'Audit Trail', icon: '🛡️' },
  ];

  return (
    <div style={{ minHeight: 'calc(100vh - var(--header-height))', backgroundColor: 'var(--bg-primary)', paddingBottom: 60 }}>
      {/* Admin Subheader */}
      <div
        style={{
          backgroundColor: 'rgba(13, 18, 29, 0.95)',
          borderBottom: '1px solid var(--border-medium)',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 'var(--header-height)',
          zIndex: 90,
        }}
      >
        <div className="container" style={{ paddingTop: 16, paddingBottom: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <VynkLogo variant="symbol" size={28} />
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
                    Vynk Admin Console
                  </span>
                  <Badge variant="indigo">Governance & Moderation</Badge>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  Platform Integrity · Telemetry · Audit Logging
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 12, color: 'var(--brand-emerald)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--brand-emerald)', display: 'inline-block', boxShadow: '0 0 8px var(--brand-emerald)' }} />
                Audit Trail Active
              </span>
            </div>
          </div>

          {/* Subnav Tabs */}
          <nav style={{ display: 'flex', gap: 4, overflowX: 'auto', paddingBottom: 2 }}>
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 18px',
                  fontSize: 13,
                  fontWeight: 600,
                  textDecoration: 'none',
                  color: isActive ? 'var(--brand-cyan)' : 'var(--text-secondary)',
                  borderBottom: isActive ? '2px solid var(--brand-cyan)' : '2px solid transparent',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap',
                })}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Admin View Container */}
      <div className="container" style={{ paddingTop: 32 }}>
        {children || <Outlet />}
      </div>
    </div>
  );
}

export default AdminLayout;
