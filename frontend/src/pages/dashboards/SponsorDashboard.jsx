import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { TrustScoreBreakdownModal } from '../../components/trust/TrustScoreBreakdownModal';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { VynkLogo } from '../../components/common/VynkLogo';
import { ProjectCard } from '../../components/project/ProjectCard';
import { MatchExplanationModal } from '../../components/ai/MatchExplanationModal';
import { SponsorshipRequestsList } from '../../components/sponsorship/SponsorshipRequestsList';
import { formatCurrency } from '../../utils/currency';

export function SponsorDashboard() {
  const { user } = useAuth();
  const [commitments, setCommitments] = useState([]);
  const [sponsorshipRequests, setSponsorshipRequests] = useState([]);
  const [followUps, setFollowUps] = useState([]);
  const [discoveredProjects, setDiscoveredProjects] = useState([]);
  const [trustScore, setTrustScore] = useState(null);
  const [isTrustModalOpen, setIsTrustModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // AI Matching State
  const [recommendedProjects, setRecommendedProjects] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [explanationModal, setExplanationModal] = useState({ isOpen: false, projectId: null });

  // Commitment Creation Modal
  const [selectedProject, setSelectedProject] = useState(null);
  const [amount, setAmount] = useState(250000);
  const [sponsorshipType, setSponsorshipType] = useState('grant');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  const loadDashboardData = async () => {
    try {
      const [commRes, reqsRes, followRes, projRes, trustRes, recsRes] = await Promise.all([
        apiRequest('/commitments/').catch(() => []),
        apiRequest('/sponsorship-requests/').catch(() => []),
        apiRequest('/commitments/follow-ups').catch(() => []),
        apiRequest('/projects/').catch(() => []),
        apiRequest('/trust/me').catch(() => null),
        apiRequest('/ai/matches/projects?limit=6').catch(() => []),
      ]);
      setCommitments(commRes);
      setSponsorshipRequests(reqsRes || []);
      setFollowUps(followRes);
      setDiscoveredProjects(projRes);
      setTrustScore(trustRes);
      setRecommendedProjects(recsRes || []);
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
              <VynkLogo variant="symbol" size={24} />
              <Badge variant="emerald">Sponsor & Fund Portal</Badge>
              <Badge variant="cyan">{user?.sponsor_profile?.sponsor_type || 'Angel Sponsor'}</Badge>
            </div>
            <h1 style={{ fontSize: 26, marginBottom: 4 }}>
              {user?.sponsor_profile?.organization_name || user?.full_name}
            </h1>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Budget Range: <strong style={{ color: 'var(--text-primary)' }}>{formatCurrency(user?.sponsor_profile?.min_budget, user?.sponsor_profile?.currency || 'INR')} – {formatCurrency(user?.sponsor_profile?.max_budget, user?.sponsor_profile?.currency || 'INR')}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <TrustScoreBadge
              score={trustScore?.score ?? user?.trust_score?.score ?? 50}
              size="md"
              onClick={() => setIsTrustModalOpen(true)}
            />
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
                        <strong style={{ fontSize: 16, color: (c.amount || 0) > 0 ? 'var(--brand-emerald)' : 'var(--brand-cyan)' }}>
                          {(c.amount || 0) > 0 ? formatCurrency(c.amount, c.currency || 'INR') : 'Non-Monetary'}
                        </strong>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
                          {c.sponsorship_type}
                        </span>
                        {c.is_overdue && (
                          <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, backgroundColor: 'rgba(244, 63, 94, 0.2)', color: 'var(--brand-rose)', fontWeight: 700, marginLeft: 8 }}>
                            OVERDUE
                          </span>
                        )}
                      </div>
                      <Badge variant={c.status === 'completed' ? 'emerald' : c.status === 'cancelled' ? 'rose' : c.status === 'confirmed' ? 'cyan' : 'amber'}>
                        {c.status}
                      </Badge>
                    </div>

                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>
                      {c.project_title || `Project #${c.project_id}`} · Founder: {c.entrepreneur_name || 'Founder'}
                    </div>

                    {c.notes && (
                      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
                        "{c.notes}"
                      </p>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 10 }}>
                      <Link to={`/commitments/${c.id}`} style={{ textDecoration: 'none' }}>
                        <Button size="sm" variant="secondary">
                          View & Progress Lifecycle →
                        </Button>
                      </Link>
                    </div>
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

            <Button
              size="sm"
              variant="secondary"
              onClick={() => setIsTrustModalOpen(true)}
              style={{ width: '100%', marginTop: 16 }}
            >
              View Auditable Breakdown & History →
            </Button>
          </div>
        </div>

        {/* INCOMING SPONSORSHIP REQUESTS SECTION */}

        <div style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>📥</span>
                <h2 style={{ fontSize: 20, margin: 0 }}>Incoming Sponsorship Inquiries ({sponsorshipRequests.length})</h2>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                Review and evaluate sponsorship pitches submitted directly to your fund.
              </p>
            </div>
          </div>

          <SponsorshipRequestsList
            requests={sponsorshipRequests}
            userRole="sponsor"
            onRefresh={loadDashboardData}
          />
        </div>

        {/* AI Recommended Projects Section */}
        <div style={{ marginBottom: 40 }}>

          <div
            style={{
              padding: '24px 28px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: 16 }}>✨</span>
                  <Badge variant="emerald">Deterministic Multi-Factor Matching</Badge>
                  <Badge variant="cyan">Gemini Explainability</Badge>
                </div>
                <h2 style={{ fontSize: 22, margin: '4px 0' }}>AI Recommended Projects</h2>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 640 }}>
                  Curated startup showcases mathematically scored against your sponsorship criteria, budget, and stage preferences. Compatibility Score is evaluated independently from Founder Trust Score.
                </p>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'right' }}>
                <div>6-Factor Compatibility Model</div>
                <div style={{ color: 'var(--brand-emerald)', fontWeight: 600 }}>100% Deterministic Base</div>
              </div>
            </div>
          </div>

          {isLoadingRecommendations ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
              <div className="spinner" style={{ width: 32, height: 32 }} />
            </div>
          ) : recommendedProjects.length === 0 ? (
            <div
              className="card"
              style={{
                padding: '36px 24px',
                textAlign: 'center',
                backgroundColor: 'rgba(13, 18, 29, 0.4)',
                border: '1px dashed var(--border-subtle)',
                marginBottom: 24,
              }}
            >
              <div style={{ fontSize: 28, marginBottom: 8 }}>🎯</div>
              <h4 style={{ fontSize: 16, marginBottom: 6 }}>No direct recommendation matches yet</h4>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 440, margin: '0 auto' }}>
                As more entrepreneurs publish startup showcases aligned with your stage and budget criteria, they will be ranked here.
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20, marginBottom: 32 }}>
              {recommendedProjects.map((rec) => {
                const score = Math.round(rec.compatibility_score);
                const scoreColor = score >= 75 ? 'var(--brand-emerald)' : score >= 50 ? 'var(--brand-cyan)' : 'var(--brand-amber)';
                return (
                  <div
                    key={rec.project_id}
                    className="card"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    {/* Top Glow Accent */}
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 3,
                        background: `linear-gradient(90deg, ${scoreColor} 0%, transparent 100%)`,
                      }}
                    />

                    <div>
                      {/* Header with Title and Badges */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 12 }}>
                        <div>
                          <Link
                            to={`/projects/${rec.project_id}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            <h3 style={{ fontSize: 18, fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)' }}>
                              {rec.title}
                            </h3>
                          </Link>
                          {rec.founder_name && (
                            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                              by {rec.founder_name}
                            </div>
                          )}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
                          <span
                            style={{
                              padding: '4px 10px',
                              borderRadius: 'var(--radius-full)',
                              fontSize: 12,
                              fontWeight: 800,
                              backgroundColor: 'rgba(16, 185, 129, 0.12)',
                              color: scoreColor,
                              border: `1px solid ${scoreColor}44`,
                            }}
                          >
                            {score}% Match
                          </span>
                        </div>
                      </div>

                      {rec.tagline && (
                        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 14, lineHeight: 1.4 }}>
                          {rec.tagline}
                        </p>
                      )}

                      {/* Industry & Stage Tags */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
                        {rec.industry && <Badge variant="cyan">{rec.industry}</Badge>}
                        {rec.stage && (
                          <Badge variant="purple" style={{ textTransform: 'capitalize' }}>
                            {rec.stage.replace('_', ' ')}
                          </Badge>
                        )}
                      </div>

                      {/* Side-by-side Score & Metrics Box */}
                      <div
                        style={{
                          padding: 12,
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'rgba(7, 9, 14, 0.6)',
                          border: '1px solid var(--border-subtle)',
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: 12,
                          marginBottom: 16,
                        }}
                      >
                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>
                            Seeking Target
                          </div>
                          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--brand-emerald)' }}>
                            {formatCurrency(rec.target_amount, rec.currency || 'INR')}
                          </div>
                        </div>

                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>
                            Founder Trust
                          </div>
                          <TrustScoreBadge score={rec.founder_trust_score ?? 50} size="sm" />
                        </div>
                      </div>

                      {/* Matching Highlights */}
                      {rec.reasons && rec.reasons.length > 0 && (
                        <div style={{ marginBottom: 16 }}>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                            Key Compatibility Signals
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            {rec.reasons.slice(0, 2).map((reason, idx) => (
                              <div
                                key={idx}
                                style={{
                                  fontSize: 12,
                                  color: 'var(--brand-emerald)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 6,
                                }}
                              >
                                <span>✓</span>
                                <span style={{ color: 'var(--text-secondary)' }}>{reason}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div style={{ display: 'flex', gap: 10, paddingTop: 14, borderTop: '1px solid var(--border-subtle)' }}>
                      <Button
                        variant="ghost"
                        size="sm"
                        style={{ flex: 1, fontSize: 12 }}
                        onClick={() => setExplanationModal({ isOpen: true, projectId: rec.project_id })}
                      >
                        ⚡ AI Breakdown
                      </Button>
                      <Button
                        variant="emerald"
                        size="sm"
                        style={{ flex: 1, fontSize: 12 }}
                        onClick={() => setSelectedProject({ id: rec.project_id, title: rec.title })}
                      >
                        Propose Support
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Discover Projects Feed */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
            <div>
              <h2 style={{ fontSize: 22 }}>Discover Startup Opportunities</h2>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                Review active projects seeking sponsorship matching your thesis.
              </p>
            </div>
            <Link to="/projects" style={{ textDecoration: 'none' }}>
              <Button variant="ghost" size="sm">
                Browse All Showcases →
              </Button>
            </Link>
          </div>

          {discoveredProjects.length === 0 ? (
            <div className="card" style={{ padding: 40, textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>No projects discovered currently.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {discoveredProjects.map((p) => (
                <ProjectCard
                  key={p.id}
                  project={p}
                  onSponsor={(proj) => setSelectedProject(proj)}
                />
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
                    <label className="form-label">Commitment Amount (₹)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      min={5000}
                      step={5000}
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

        {/* AI Explanation Modal */}
        <MatchExplanationModal
          isOpen={explanationModal.isOpen}
          onClose={() => setExplanationModal({ isOpen: false, projectId: null })}
          targetType="project"
          targetId={explanationModal.projectId}
          actionLabel="Propose Sponsorship"
          onActionClick={() => {
            const pr = recommendedProjects.find((p) => p.project_id === explanationModal.projectId);
            setExplanationModal({ isOpen: false, projectId: null });
            if (pr) {
              setSelectedProject({ id: pr.project_id, title: pr.title });
            }
          }}
        />

        {/* Trust Score Breakdown Modal */}
        <TrustScoreBreakdownModal
          isOpen={isTrustModalOpen}
          onClose={() => {
            setIsTrustModalOpen(false);
            loadDashboardData();
          }}
        />
      </div>
    </div>
  );
}
