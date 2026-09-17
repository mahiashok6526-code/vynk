import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { TrustScoreBreakdownModal } from '../../components/trust/TrustScoreBreakdownModal';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { VynkLogo } from '../../components/common/VynkLogo';
import { ProjectCard } from '../../components/project/ProjectCard';
import { MatchExplanationModal } from '../../components/ai/MatchExplanationModal';
import { ConnectModal } from '../../components/sponsor/ConnectModal';
import { SponsorshipRequestsList } from '../../components/sponsorship/SponsorshipRequestsList';
import { formatCurrency } from '../../utils/currency';

export function EntrepreneurDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [commitments, setCommitments] = useState([]);
  const [sponsorshipRequests, setSponsorshipRequests] = useState([]);
  const [trustScore, setTrustScore] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'published', 'draft', 'archived'
  const [actionAlert, setActionAlert] = useState({ type: '', text: '' });
  const [isTrustModalOpen, setIsTrustModalOpen] = useState(false);

  // AI Matching State
  const [recommendedSponsors, setRecommendedSponsors] = useState([]);
  const [selectedMatchingProjectId, setSelectedMatchingProjectId] = useState('');
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [explanationModal, setExplanationModal] = useState({ isOpen: false, sponsorId: null });
  const [connectModalSponsor, setConnectModalSponsor] = useState(null);

  const loadRecommendations = async (projId) => {
    setIsLoadingRecommendations(true);
    try {
      const url = projId ? `/ai/matches/sponsors?project_id=${projId}&limit=6` : '/ai/matches/sponsors?limit=6';
      const res = await apiRequest(url);
      setRecommendedSponsors(res || []);
    } catch (err) {
      console.error('Failed to load sponsor recommendations:', err);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      const [projectsRes, commitmentsRes, requestsRes, trustRes] = await Promise.all([
        apiRequest('/projects/my-projects').catch(() => []),
        apiRequest('/commitments/').catch(() => []),
        apiRequest('/sponsorship-requests/').catch(() => []),
        apiRequest('/trust/me').catch(() => null),
      ]);
      setProjects(projectsRes);
      setCommitments(commitmentsRes);
      setSponsorshipRequests(requestsRes || []);
      setTrustScore(trustRes);

      if (projectsRes && projectsRes.length > 0) {
        const defaultId = projectsRes[0].id;
        setSelectedMatchingProjectId(defaultId);
        loadRecommendations(defaultId);
      }
    } catch (err) {
      console.error('Error loading entrepreneur data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handlePublish = async (project) => {
    try {
      await apiRequest(`/projects/${project.id}/publish`, { method: 'POST' });
      setActionAlert({ type: 'success', text: `Project "${project.title}" published successfully!` });
      await loadDashboardData();
    } catch (err) {
      if (err.message && err.message.includes('Missing required fields')) {
        // Redirect to edit page to fill in missing fields
        navigate(`/projects/${project.id}/edit`);
      } else {
        setActionAlert({ type: 'error', text: err.message || 'Failed to publish project.' });
      }
    }
  };

  const handleArchive = async (project) => {
    if (!window.confirm(`Are you sure you want to archive "${project.title}"?`)) return;
    try {
      await apiRequest(`/projects/${project.id}/archive`, { method: 'POST' });
      setActionAlert({ type: 'success', text: `Project "${project.title}" archived.` });
      await loadDashboardData();
    } catch (err) {
      setActionAlert({ type: 'error', text: err.message || 'Failed to archive project.' });
    }
  };

  const filteredProjects = projects.filter((p) => {
    const s = (p.status || '').toLowerCase();
    if (activeTab === 'published') {
      return s === 'published' || s === 'seeking_sponsorship' || s === 'active' || s === 'in_discussion' || s === 'funded' || s === 'completed';
    }
    if (activeTab === 'draft') {
      return s === 'draft';
    }
    if (activeTab === 'archived') {
      return s === 'archived';
    }
    return true;
  });

  const publishedCount = projects.filter((p) => {
    const s = (p.status || '').toLowerCase();
    return s !== 'draft' && s !== 'archived';
  }).length;
  const draftCount = projects.filter((p) => (p.status || '').toLowerCase() === 'draft').length;
  const archivedCount = projects.filter((p) => (p.status || '').toLowerCase() === 'archived').length;

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
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(6, 182, 212, 0.08) 100%)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <VynkLogo variant="symbol" size={24} />
              <Badge variant="cyan">Entrepreneur Portal</Badge>
              {user?.is_verified ? (
                <Badge variant="emerald">Verified Account</Badge>
              ) : (
                <Badge variant="amber">Standard Member</Badge>
              )}
            </div>
            <h1 style={{ fontSize: 26, marginBottom: 4 }}>Welcome back, {user?.full_name}</h1>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Industry focus: <strong style={{ color: 'var(--text-primary)' }}>{user?.entrepreneur_profile?.industry || 'Startups & Innovation'}</strong> · Stage: <span style={{ textTransform: 'capitalize' }}>{user?.entrepreneur_profile?.stage || 'Idea'}</span>
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <TrustScoreBadge
              score={trustScore?.score ?? user?.trust_score?.score ?? 50}
              size="md"
              onClick={() => setIsTrustModalOpen(true)}
            />
            <Link to="/projects/new" style={{ textDecoration: 'none' }}>
              <Button variant="primary">
                + New Project Showcase
              </Button>
            </Link>
          </div>
        </div>

        {actionAlert.text && (
          <div className={`alert alert-${actionAlert.type}`} style={{ marginBottom: 24 }}>
            <span>{actionAlert.text}</span>
          </div>
        )}

        {/* Dashboard Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, marginBottom: 36 }}>
          {/* Trust Score Breakdown Card */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 18 }}>Trust Score Breakdown</h3>
              <TrustScoreBadge
                score={trustScore?.score ?? 50}
                size="sm"
                showLabel={false}
                onClick={() => setIsTrustModalOpen(true)}
              />
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Calculated dynamically from platform verification, fulfilled commitments, and responsive communication.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {(trustScore?.factors || [
                { name: 'Platform Verification', points: 0, max_points: 25 },
                { name: 'Commitment Reliability', points: 20, max_points: 35 },
                { name: 'Communication Responsiveness', points: 15, max_points: 20 },
                { name: 'Activity & Updates', points: 15, max_points: 20 },
              ]).map((f) => (
                <div key={f.name}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{f.name}</span>
                    <strong style={{ color: 'var(--text-primary)' }}>{f.points} / {f.max_points} pts</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${Math.min(100, (f.points / f.max_points) * 100)}%`,
                        height: '100%',
                        backgroundColor: 'var(--brand-cyan)',
                        borderRadius: 3,
                      }}
                    />
                  </div>
                </div>
              ))}
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

          {/* Commitment Tracker Pipeline */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <h3 style={{ fontSize: 18 }}>Portfolio Commitments ({commitments.length})</h3>
              <Badge variant="emerald">7-Stage Lifecycle</Badge>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Structured lifecycle of sponsor agreements backing your initiatives.
            </p>

            {commitments.length === 0 ? (
              <div style={{ padding: '30px 16px', textAlign: 'center', backgroundColor: 'rgba(7, 9, 14, 0.5)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 8 }}>No commitments recorded yet.</p>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  When a sponsor accepts your request or directly pledges backing, the commitment will appear here.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {commitments.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      padding: 14,
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'rgba(7, 9, 14, 0.7)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: 12,
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <strong style={{ fontSize: 15, color: (c.amount || 0) > 0 ? 'var(--brand-emerald)' : 'var(--brand-cyan)' }}>
                          {(c.amount || 0) > 0 ? formatCurrency(c.amount, c.currency || 'INR') : 'Non-Monetary'}
                        </strong>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>· {c.sponsorship_type}</span>
                        {c.is_overdue && (
                          <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, backgroundColor: 'rgba(244, 63, 94, 0.2)', color: 'var(--brand-rose)', fontWeight: 700 }}>
                            OVERDUE
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                        {c.project_title || `Project #${c.project_id}`} · Partner: {c.sponsor_name || c.sponsor_org || 'Sponsor'}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Badge variant={c.status === 'completed' ? 'emerald' : c.status === 'cancelled' ? 'rose' : 'cyan'}>
                        {c.status}
                      </Badge>
                      <Link to={`/commitments/${c.id}`} style={{ textDecoration: 'none' }}>
                        <Button size="sm" variant="secondary">
                          View →
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* SPONSORSHIP REQUESTS SECTION */}
        <div style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>🤝</span>
                <h2 style={{ fontSize: 20, margin: 0 }}>Sponsorship Proposals & Requests ({sponsorshipRequests.length})</h2>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                Track proposals sent to funding partners, sponsor responses, and pending decisions.
              </p>
            </div>
          </div>

          <SponsorshipRequestsList
            requests={sponsorshipRequests}
            userRole="entrepreneur"
            onRefresh={loadDashboardData}
          />
        </div>

        {/* AI RECOMMENDED SPONSORS SECTION */}
        {projects.length > 0 && (
          <div style={{ marginBottom: 36 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 20 }}>✨</span>
                  <h2 style={{ fontSize: 22, margin: 0 }}>Recommended Capital Partners</h2>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 999,
                      backgroundColor: 'rgba(6, 182, 212, 0.15)',
                      color: 'var(--brand-cyan)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                    }}
                  >
                    AI Match Engine
                  </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                  Intelligently ranked sponsors aligned with your venture's industry, stage, and funding requirement.
                </p>
              </div>

              {projects.length > 1 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <label style={{ fontSize: 12, color: 'var(--text-muted)' }}>Match for:</label>
                  <select
                    className="input"
                    value={selectedMatchingProjectId}
                    onChange={(e) => {
                      setSelectedMatchingProjectId(e.target.value);
                      loadRecommendations(e.target.value);
                    }}
                    style={{ padding: '6px 12px', fontSize: 13, minWidth: 200 }}
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {isLoadingRecommendations ? (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
                <div className="spinner" style={{ width: 28, height: 28, margin: '0 auto 12px auto' }} />
                <p style={{ fontSize: 13 }}>Computing compatibility rankings...</p>
              </div>
            ) : recommendedSponsors.length === 0 ? (
              <div className="card" style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>
                <p style={{ margin: 0, fontSize: 14 }}>
                  No sponsor recommendations found for this project criteria yet.
                </p>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 20 }}>
                {recommendedSponsors.map((match) => (
                  <div
                    key={match.sponsor_id}
                    className="card"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      padding: 20,
                      position: 'relative',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                    }}
                  >
                    <div>
                      {/* Top Row: Compatibility Badge & Verified */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div
                            style={{
                              width: 44,
                              height: 44,
                              borderRadius: 10,
                              backgroundColor: 'rgba(6, 182, 212, 0.1)',
                              border: '1px solid rgba(6, 182, 212, 0.2)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 20,
                              color: 'var(--brand-cyan)',
                              fontWeight: 700,
                            }}
                          >
                            {(match.organization_name || match.full_name || 'S')[0].toUpperCase()}
                          </div>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                              <h4 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                                {match.organization_name || match.full_name}
                              </h4>
                              {match.is_verified && (
                                <span title="Verified Sponsor" style={{ color: 'var(--brand-emerald)', fontSize: 14 }}>
                                  ✓
                                </span>
                              )}
                            </div>
                            <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                              {(match.sponsor_type || 'angel').replace('_', ' ')}
                            </span>
                          </div>
                        </div>

                        {/* Match Badge */}
                        <div
                          style={{
                            padding: '4px 10px',
                            borderRadius: 999,
                            backgroundColor: match.compatibility_score >= 80 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                            border: `1px solid ${match.compatibility_score >= 80 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(6, 182, 212, 0.3)'}`,
                            color: match.compatibility_score >= 80 ? 'var(--brand-emerald)' : 'var(--brand-cyan)',
                            fontSize: 12,
                            fontWeight: 800,
                          }}
                        >
                          {match.compatibility_score}% Match
                        </div>
                      </div>

                      {/* Ticket Size & Reliability */}
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '8px 12px',
                          borderRadius: 8,
                          backgroundColor: 'rgba(255, 255, 255, 0.03)',
                          marginBottom: 12,
                          fontSize: 12,
                        }}
                      >
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Ticket Size: </span>
                          <span style={{ fontWeight: 600, color: 'var(--brand-emerald)' }}>
                            {formatCurrency(match.min_budget, 'INR', true)} – {formatCurrency(match.max_budget, 'INR', true)}
                          </span>
                        </div>
                        <TrustScoreBadge score={match.trust_score} size="sm" />
                      </div>

                      {/* Top Match Reasons */}
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontSize: 11, textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: 6 }}>
                          Key Compatibility Drivers
                        </div>
                        <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
                          {(match.reasons || []).slice(0, 3).map((r, i) => (
                            <li key={i}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: 14 }}>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setExplanationModal({ isOpen: true, sponsorId: match.sponsor_id, sponsorName: match.organization_name || match.full_name })}
                        style={{ fontSize: 12, padding: '6px 10px' }}
                      >
                        ⚡ AI Breakdown
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => setConnectModalSponsor(match)}
                        style={{ fontSize: 12, padding: '6px 10px' }}
                      >
                        Connect
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* My Projects Showcase Section */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
            <div>
              <h2 style={{ fontSize: 22 }}>My Projects & Startups</h2>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                Manage your venture showcases, drafts, and sponsorship discovery status.
              </p>
            </div>

            <Link to="/projects/new" style={{ textDecoration: 'none' }}>
              <Button variant="primary" size="sm">
                + New Project Showcase
              </Button>
            </Link>
          </div>

          {/* Status Tabs */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 20, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 10 }}>
            {[
              { key: 'all', label: 'All Projects', count: projects.length },
              { key: 'published', label: 'Published', count: publishedCount },
              { key: 'draft', label: 'Drafts', count: draftCount },
              { key: 'archived', label: 'Archived', count: archivedCount },
            ].map((tab) => {
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '8px 14px',
                    borderRadius: 'var(--radius-md)',
                    fontSize: 13,
                    fontWeight: isActive ? 700 : 500,
                    color: isActive ? 'var(--brand-cyan)' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'rgba(6, 182, 212, 0.1)' : 'transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <span>{tab.label}</span>
                  <span
                    style={{
                      fontSize: 11,
                      padding: '1px 6px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: isActive ? 'var(--brand-cyan)' : 'rgba(255, 255, 255, 0.08)',
                      color: isActive ? '#07090E' : 'var(--text-muted)',
                      fontWeight: 700,
                    }}
                  >
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Projects Content Grid */}
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
              <div className="spinner" style={{ width: 32, height: 32 }} />
            </div>
          ) : filteredProjects.length === 0 ? (
            <div
              className="card"
              style={{
                padding: '48px 24px',
                textAlign: 'center',
                backgroundColor: 'rgba(13, 18, 29, 0.5)',
                border: '1px dashed var(--border-subtle)',
              }}
            >
              <div style={{ width: 48, height: 48, borderRadius: '50%', backgroundColor: 'rgba(6, 182, 212, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--brand-cyan)', fontSize: 22 }}>
                💡
              </div>
              <h3 style={{ fontSize: 18, marginBottom: 8 }}>
                {activeTab === 'draft' ? 'No Draft Projects' : activeTab === 'archived' ? 'No Archived Projects' : 'No Projects Found'}
              </h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto 20px' }}>
                {activeTab === 'draft'
                  ? 'You do not have any unfinished draft projects saved.'
                  : activeTab === 'archived'
                  ? 'You have not archived any projects.'
                  : 'Create your first project showcase so sponsors can discover your innovation and propose structured commitments.'}
              </p>
              <Link to="/projects/new">
                <Button variant="primary">
                  Create Project Showcase
                </Button>
              </Link>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 20 }}>
              {filteredProjects.map((p) => (
                <ProjectCard
                  key={p.id}
                  project={p}
                  isOwner={true}
                  onPublish={handlePublish}
                  onArchive={handleArchive}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* AI Explanation Modal */}
      <MatchExplanationModal
        isOpen={explanationModal.isOpen}
        onClose={() => setExplanationModal({ isOpen: false, sponsorId: null })}
        targetType="sponsor"
        targetId={explanationModal.sponsorId}
        projectId={selectedMatchingProjectId}
        actionLabel="Initiate Connection"
        onActionClick={() => {
          const sp = recommendedSponsors.find((s) => s.sponsor_id === explanationModal.sponsorId);
          setExplanationModal({ isOpen: false, sponsorId: null });
          if (sp) {
            setConnectModalSponsor({
              id: sp.sponsor_id,
              company_name: sp.company_name,
              min_budget: sp.min_budget,
              max_budget: sp.max_budget,
            });
          }
        }}
      />

      {/* Connect Modal */}
      {connectModalSponsor && (
        <ConnectModal
          sponsor={connectModalSponsor}
          onClose={() => setConnectModalSponsor(null)}
          onSuccess={() => {
            setConnectModalSponsor(null);
            setActionAlert({ type: 'success', text: `Connection request submitted to ${connectModalSponsor.company_name || 'sponsor'}!` });
          }}
        />
      )}

      {/* Trust Score Breakdown Modal */}
      <TrustScoreBreakdownModal
        isOpen={isTrustModalOpen}
        onClose={() => {
          setIsTrustModalOpen(false);
          loadDashboardData();
        }}
      />
    </div>
  );
}

