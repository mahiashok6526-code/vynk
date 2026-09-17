import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';

export function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await adminService.getAdminDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load admin stats:', err);
      setError(err.message || 'Failed to load telemetry stats');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <div className="spinner" style={{ width: 36, height: 36 }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 40 }}>
        <div style={{ color: 'var(--brand-rose)', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
          Telemetry Unavailable
        </div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>{error}</p>
        <button onClick={loadDashboard} className="btn btn-secondary btn-sm">
          Retry
        </button>
      </div>
    );
  }

  const users = stats?.users || {};
  const projects = stats?.projects || {};
  const sponsorships = stats?.sponsorships || {};
  const trust = stats?.trust || {};
  const queues = stats?.queues || {};
  const recentLogs = stats?.recent_audit_logs || [];

  return (
    <div>
      {/* Top Banner with Quick Actions */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(99, 102, 241, 0.15) 100%)',
          marginBottom: 28,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 20,
        }}
      >
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 6 }}>Platform Governance Dashboard</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Real-time telemetry, moderation workflows, and cryptographic-grade audit logs.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Link to="/admin/users" className="btn btn-secondary btn-sm">
            👥 Manage Users
          </Link>
          <Link to="/admin/projects" className="btn btn-secondary btn-sm">
            🚀 Review Projects
          </Link>
          <Link to="/admin/reports" className="btn btn-secondary btn-sm">
            ⚠️ Reports ({queues.pending_reports || 0})
          </Link>
          <Link to="/admin/disputes" className="btn btn-secondary btn-sm">
            ⚖️ Disputes ({queues.open_disputes || 0})
          </Link>
        </div>
      </div>

      {/* Moderation Alert Bar if items in queue */}
      {(queues.pending_verifications > 0 || queues.pending_reports > 0 || queues.open_disputes > 0 || queues.pending_projects > 0) && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 16,
            marginBottom: 28,
          }}
        >
          <div
            className="card"
            style={{
              borderColor: queues.pending_verifications > 0 ? 'rgba(245, 158, 11, 0.4)' : 'var(--border-subtle)',
              backgroundColor: queues.pending_verifications > 0 ? 'rgba(245, 158, 11, 0.06)' : 'var(--bg-glass)',
              padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Pending Verifications</span>
              <Badge variant={queues.pending_verifications > 0 ? 'amber' : 'secondary'}>
                {queues.pending_verifications || 0}
              </Badge>
            </div>
            <div style={{ marginTop: 8 }}>
              <Link to="/admin/users" style={{ fontSize: 12, color: 'var(--brand-cyan)', fontWeight: 600 }}>
                Review verification queue →
              </Link>
            </div>
          </div>

          <div
            className="card"
            style={{
              borderColor: queues.pending_projects > 0 ? 'rgba(6, 182, 212, 0.4)' : 'var(--border-subtle)',
              backgroundColor: queues.pending_projects > 0 ? 'rgba(6, 182, 212, 0.06)' : 'var(--bg-glass)',
              padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Projects Pending Review</span>
              <Badge variant={queues.pending_projects > 0 ? 'cyan' : 'secondary'}>
                {queues.pending_projects || 0}
              </Badge>
            </div>
            <div style={{ marginTop: 8 }}>
              <Link to="/admin/projects" style={{ fontSize: 12, color: 'var(--brand-cyan)', fontWeight: 600 }}>
                Moderate showcases →
              </Link>
            </div>
          </div>

          <div
            className="card"
            style={{
              borderColor: queues.pending_reports > 0 ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)',
              backgroundColor: queues.pending_reports > 0 ? 'rgba(244, 63, 94, 0.06)' : 'var(--bg-glass)',
              padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Flagged Reports</span>
              <Badge variant={queues.pending_reports > 0 ? 'rose' : 'secondary'}>
                {queues.pending_reports || 0}
              </Badge>
            </div>
            <div style={{ marginTop: 8 }}>
              <Link to="/admin/reports" style={{ fontSize: 12, color: 'var(--brand-rose)', fontWeight: 600 }}>
                Inspect reports queue →
              </Link>
            </div>
          </div>

          <div
            className="card"
            style={{
              borderColor: queues.open_disputes > 0 ? 'rgba(139, 92, 246, 0.4)' : 'var(--border-subtle)',
              backgroundColor: queues.open_disputes > 0 ? 'rgba(139, 92, 246, 0.06)' : 'var(--bg-glass)',
              padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Active Disputes</span>
              <Badge variant={queues.open_disputes > 0 ? 'indigo' : 'secondary'}>
                {queues.open_disputes || 0}
              </Badge>
            </div>
            <div style={{ marginTop: 8 }}>
              <Link to="/admin/disputes" style={{ fontSize: 12, color: 'var(--brand-indigo)', fontWeight: 600 }}>
                Arbitrate commitments →
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Primary Telemetry Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20, marginBottom: 28 }}>
        {/* User Stats Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              User Base
            </span>
            <Badge variant="cyan">{users.total || 0} Total</Badge>
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8 }}>
            {users.total || 0}
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Entrepreneurs:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{users.entrepreneurs || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Sponsors:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{users.sponsors || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Verified Accounts:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-emerald)' }}>{users.verified || 0}</span>
            </div>
            {users.suspended > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Suspended:</span>
                <span style={{ fontWeight: 600, color: 'var(--brand-rose)' }}>{users.suspended}</span>
              </div>
            )}
          </div>
        </div>

        {/* Project Stats Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Showcase Projects
            </span>
            <Badge variant="emerald">{projects.published || 0} Live</Badge>
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, color: 'var(--brand-cyan)', marginBottom: 8 }}>
            {projects.total || 0}
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Published:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{projects.published || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Drafts:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>{projects.draft || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Approved Moderation:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-emerald)' }}>{projects.approved || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Rejected / Flagged:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-rose)' }}>{projects.rejected || 0}</span>
            </div>
          </div>
        </div>

        {/* Sponsorship Stats Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Sponsorship Volume
            </span>
            <Badge variant="emerald">${(sponsorships.total_volume_usd || 0).toLocaleString()}</Badge>
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, color: 'var(--brand-emerald)', marginBottom: 8 }}>
            {sponsorships.total_commitments || 0}
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Active Commitments:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{sponsorships.active || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Fulfilled:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-emerald)' }}>{sponsorships.completed || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>In Dispute:</span>
              <span style={{ fontWeight: 600, color: sponsorships.disputed > 0 ? 'var(--brand-rose)' : 'var(--text-muted)' }}>
                {sponsorships.disputed || 0}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Proposals Tracked:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{sponsorships.total_requests || 0}</span>
            </div>
          </div>
        </div>

        {/* Platform Trust Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Trust Index
            </span>
            <Badge variant="amber">Phase 7 Algorithmic</Badge>
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, color: '#F59E0B', marginBottom: 8 }}>
            {trust.average_trust_score ?? 50}
            <span style={{ fontSize: 14, color: 'var(--text-muted)', fontWeight: 500 }}>/100</span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Highest Score:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-emerald)' }}>{trust.highest_trust_score ?? 50}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Lowest Score:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{trust.lowest_trust_score ?? 50}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Scoring Rules:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-cyan)' }}>Deterministic 5-Pillar</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Manual Overrides:</span>
              <span style={{ fontWeight: 600, color: 'var(--brand-rose)' }}>Disabled (Strict)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Audit Trail Feed */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontSize: 18, marginBottom: 4 }}>Recent Administrative Actions</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Immutable audit events recorded with verified admin identity.
            </p>
          </div>
          <Link to="/admin/audit-logs" className="btn btn-secondary btn-sm">
            View All Logs →
          </Link>
        </div>

        {recentLogs.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
            No administrative events recorded yet.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '10px 12px' }}>Timestamp</th>
                  <th style={{ padding: '10px 12px' }}>Admin</th>
                  <th style={{ padding: '10px 12px' }}>Action</th>
                  <th style={{ padding: '10px 12px' }}>Target</th>
                  <th style={{ padding: '10px 12px' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {log.admin?.full_name || log.admin_id.slice(0, 8)}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <Badge variant={log.action.includes('suspend') || log.action.includes('reject') ? 'rose' : 'cyan'}>
                        {log.action}
                      </Badge>
                    </td>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>
                      {log.entity_type} #{log.entity_id ? log.entity_id.slice(0, 8) : 'N/A'}
                    </td>
                    <td style={{ padding: '12px', color: 'var(--text-muted)', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {log.details ? JSON.stringify(log.details) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboardPage;
