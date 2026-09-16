import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export function SponsorDashboard() {
  const { user } = useAuth();
  const [commitments, setCommitments] = useState([]);
  const [followUps, setFollowUps] = useState([]);
  const [discoveredProjects, setDiscoveredProjects] = useState([]);
  const [trustScore, setTrustScore] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Commitment Creation Modal
  const [selectedProject, setSelectedProject] = useState(null);
  const [amount, setAmount] = useState(25000);
  const [sponsorshipType, setSponsorshipType] = useState('grant');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  const loadDashboardData = async () => {
    try {
      const [commRes, followRes, projRes, trustRes] = await Promise.all([
        apiRequest('/commitments/').catch(() => []),
        apiRequest('/commitments/follow-ups').catch(() => []),
        apiRequest('/projects/').catch(() => []),
        apiRequest('/trust/me').catch(() => null),
      ]);
      setCommitments(commRes);
      setFollowUps(followRes);
      setDiscoveredProjects(projRes);
      setTrustScore(trustRes);
    } catch (err) {
      console.error('Error loading sponsor dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleCreateCommitment = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    setIsSubmitting(true);
    setActionMessage('');

    try {
      await apiRequest('/commitments/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: selectedProject.id,
          amount: Number(amount),
          sponsorship_type: sponsorshipType,
          status: 'interested',
          notes: notes.trim() || undefined,
        }),
      });
      setSelectedProject(null);
      setNotes('');
      setActionMessage('Commitment successfully recorded in your portfolio pipeline!');
      await loadDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to record commitment.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProgressStatus = async (commitmentId, newStatus) => {
    try {
      await apiRequest(`/commitments/${commitmentId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({
          new_status: newStatus,
          note: `Advanced milestone to ${newStatus}.`,
        }),
      });
      await loadDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to update commitment status.');
    }
  };

  return (
    <div className="section" style={{ paddingTop: 30, minHeight: '80vh' }}>
      <div className="container">
        {/* Header Profile Bar */}
        <div
          className="card"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 20,
            marginBottom: 32,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(16, 185, 129, 0.08) 100%)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <Badge variant="emerald">Sponsor & Fund Portal</Badge>
              <Badge variant="cyan">{user?.sponsor_profile?.sponsor_type || 'Angel Sponsor'}</Badge>
            </div>
            <h1 style={{ fontSize: 26, marginBottom: 4 }}>
              {user?.sponsor_profile?.organization_name || user?.full_name}
            </h1>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Budget Range: <strong style={{ color: 'var(--text-primary)' }}>${user?.sponsor_profile?.min_budget?.toLocaleString()} - ${user?.sponsor_profile?.max_budget?.toLocaleString()}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <TrustScoreBadge score={trustScore?.score ?? user?.trust_score?.score ?? 50} size="md" />
          </div>
        </div>

        {actionMessage && (
          <div className="alert alert-success">
            <span>{actionMessage}</span>
          </div>
        )}

        {/* Dashboard Portfolio Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, marginBottom: 36 }}>
          {/* Active Sponsorship Commitments */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 18 }}>Portfolio Commitments ({commitments.length})</h3>
              <Badge variant="emerald">7-Stage Lifecycle</Badge>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Audit-logged milestones tracking your sponsorship agreements.
            </p>

            {commitments.length === 0 ? (
              <div style={{ padding: '30px 16px', textAlign: 'center', backgroundColor: 'rgba(7, 9, 14, 0.5)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>No commitments logged yet.</p>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                  Browse projects below and initiate a structured sponsorship record.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {commitments.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      padding: 16,
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'rgba(7, 9, 14, 0.7)',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <div>
                        <strong style={{ fontSize: 16, color: 'var(--brand-emerald)' }}>
                          ${c.amount.toLocaleString()}
                        </strong>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
                          {c.sponsorship_type}
                        </span>
                      </div>
                      <Badge variant={c.status === 'completed' ? 'emerald' : c.status === 'confirmed' ? 'cyan' : 'amber'}>
                        {c.status}
                      </Badge>
                    </div>

                    {c.notes && (
                      <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
                        "{c.notes}"
                      </p>
                    )}

                    {/* Progression Action */}
                    {c.status !== 'completed' && c.status !== 'cancelled' && (
                      <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                        {c.status === 'interested' && (
                          <Button size="sm" variant="secondary" onClick={() => handleProgressStatus(c.id, 'discussion')}>
                            Move to Discussion →
                          </Button>
                        )}
                        {c.status === 'discussion' && (
                          <Button size="sm" variant="secondary" onClick={() => handleProgressStatus(c.id, 'promised')}>
                            Advance to Promised →
                          </Button>
                        )}
                        {c.status === 'promised' && (
                          <Button size="sm" variant="primary" onClick={() => handleProgressStatus(c.id, 'confirmed')}>
                            Confirm Agreement →
                          </Button>
                        )}
                        {c.status === 'confirmed' && (
                          <Button size="sm" variant="emerald" onClick={() => handleProgressStatus(c.id, 'completed')}>
                            Mark Fully Funded & Completed ✓
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Follow-ups & Reliability Metric */}
          <div className="card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Follow-Up Schedule & Reliability</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Timely responses directly preserve and increase your Sponsor Trust Score.
            </p>

            <div style={{ padding: 18, borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', border: '1px solid var(--border-subtle)', marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Sponsor Trust Rating:</span>
                <strong style={{ color: '#10B981' }}>{trustScore?.score ?? 50}/100</strong>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {trustScore?.completed_commitments_count || 0} successfully fulfilled agreements recorded on platform.
              </div>
            </div>

            <h4 style={{ fontSize: 14, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 10 }}>
              Commitment Lifecycle Phases
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
              <div>1. <strong>Interested:</strong> Initial mutual interest flagged.</div>
              <div>2. <strong>Discussion:</strong> Term alignment and technical evaluation.</div>
              <div>3. <strong>Promised:</strong> Term sheet or verbal allocation committed.</div>
              <div>4. <strong>Confirmed:</strong> Formal agreement executed.</div>
              <div>5. <strong>Completed:</strong> Capital or resources disbursed.</div>
            </div>
          </div>
        </div>

        {/* Discover Projects Feed */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <h2 style={{ fontSize: 22 }}>Discover Startup Opportunities</h2>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                Review active projects seeking sponsorship matching your thesis.
              </p>
            </div>
          </div>

          {discoveredProjects.length === 0 ? (
            <div className="card" style={{ padding: 40, textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>No projects discovered currently.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {discoveredProjects.map((p) => (
                <div key={p.id} className="card card-hover">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <Badge variant="cyan">{p.category}</Badge>
                    <Badge variant="indigo">{p.stage}</Badge>
                  </div>
                  <h3 style={{ fontSize: 18, marginBottom: 6 }}>{p.title}</h3>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 14 }}>{p.tagline}</p>
                  <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, fontSize: 13 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Seeking Capital:</span>
                    <strong style={{ color: 'var(--brand-emerald)' }}>${p.funding_goal.toLocaleString()}</strong>
                  </div>
                  <Button
                    variant="emerald"
                    size="sm"
                    style={{ width: '100%' }}
                    onClick={() => setSelectedProject(p)}
                  >
                    Propose Sponsorship Commitment
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Propose Commitment Modal */}
        {selectedProject && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(7, 9, 14, 0.85)',
              backdropFilter: 'blur(8px)',
              zIndex: 200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 20,
            }}
          >
            <div className="card" style={{ maxWidth: 520, width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontSize: 20 }}>Create Sponsorship Commitment</h3>
                <button
                  onClick={() => setSelectedProject(null)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <div style={{ padding: 14, backgroundColor: 'rgba(6, 182, 212, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(6, 182, 212, 0.2)', marginBottom: 20 }}>
                <div style={{ fontSize: 12, color: 'var(--brand-cyan)', fontWeight: 700 }}>TARGET PROJECT</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>{selectedProject.title}</div>
              </div>

              <form onSubmit={handleCreateCommitment}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Commitment Amount ($)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      min={500}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Sponsorship Type</label>
                    <select
                      className="form-select"
                      value={sponsorshipType}
                      onChange={(e) => setSponsorshipType(e.target.value)}
                    >
                      <option value="grant">Non-Dilutive Grant</option>
                      <option value="equity">Equity Sponsorship</option>
                      <option value="convertible_note">Convertible Note</option>
                      <option value="credits">Cloud / Infra Credits</option>
                      <option value="mentorship">Strategic Mentorship</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Commitment Notes & Terms</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    placeholder="Specify allocation expectations, milestones, or discussion timeline..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                  <Button variant="ghost" onClick={() => setSelectedProject(null)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="emerald" isLoading={isSubmitting}>
                    Record Commitment
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
