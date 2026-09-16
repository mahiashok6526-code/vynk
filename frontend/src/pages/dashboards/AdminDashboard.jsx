import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { Badge } from '../../components/common/Badge';
import { VynkLogo } from '../../components/common/VynkLogo';

export function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await apiRequest('/admin/stats');
        setStats(data);
      } catch (err) {
        console.warn('Could not load admin stats:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="section" style={{ paddingTop: 30, minHeight: '80vh' }}>
      <div className="container">
        <div
          className="card"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 20,
            marginBottom: 32,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(99, 102, 241, 0.12) 100%)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <VynkLogo variant="symbol" size={24} />
              <Badge variant="indigo">Admin & Moderation Portal</Badge>
            </div>
            <h1 style={{ fontSize: 26, marginBottom: 4 }}>Platform Governance</h1>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Live telemetry, verification queues, and dispute moderation.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20, marginBottom: 32 }}>
          <div className="card">
            <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Users</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>
              {stats?.users?.total ?? 0}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              {stats?.users?.entrepreneurs ?? 0} Founders · {stats?.users?.sponsors ?? 0} Sponsors
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Live Projects</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--brand-cyan)', marginTop: 4 }}>
              {stats?.projects_count ?? 0}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Showcased & active
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Commitments Tracked</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--brand-emerald)', marginTop: 4 }}>
              {stats?.commitments?.total_count ?? 0}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              ${(stats?.commitments?.total_funding_usd ?? 0).toLocaleString()} volume
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Platform Avg Trust</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: '#F59E0B', marginTop: 4 }}>
              {stats?.average_trust_score ?? 50.0}
              <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>/100</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Verifiable credibility index
            </div>
          </div>
        </div>

        {/* Queues */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
          <div className="card">
            <h3 style={{ fontSize: 18, marginBottom: 12 }}>Verification Queue</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Identity documents and accredited investor accreditation reviews.
            </p>
            <div style={{ padding: 20, textAlign: 'center', backgroundColor: 'rgba(7, 9, 14, 0.5)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                {stats?.queue?.pending_verifications ?? 0} pending verification requests
              </span>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 18, marginBottom: 12 }}>Reported Content & Disputes</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Project compliance and user conduct reports.
            </p>
            <div style={{ padding: 20, textAlign: 'center', backgroundColor: 'rgba(7, 9, 14, 0.5)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                {stats?.queue?.pending_reports ?? 0} active moderation flags
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
