import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { formatCurrency } from '../../utils/currency';

export function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [project, setProject] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Sponsor Commitment Proposal Modal State
  const [showSponsorModal, setShowSponsorModal] = useState(false);
  const [amount, setAmount] = useState(250000);
  const [sponsorshipType, setSponsorshipType] = useState('grant');
  const [notes, setNotes] = useState('');
  const [isSubmittingProposal, setIsSubmittingProposal] = useState(false);
  const [proposalSuccess, setProposalSuccess] = useState('');

  useEffect(() => {
    async function loadProjectDetails() {
      setIsLoading(true);
      setError('');
      try {
        const data = await apiRequest(`/projects/${id}`);
        setProject(data);
      } catch (err) {
        setError(err.message || 'Project not found.');
      } finally {
        setIsLoading(false);
      }
    }
    loadProjectDetails();
  }, [id]);

  const handleProposeCommitment = async (e) => {
    e.preventDefault();
    setIsSubmittingProposal(true);
    setProposalSuccess('');

    try {
      await apiRequest('/commitments/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: project.id,
          amount: Number(amount),
          sponsorship_type: sponsorshipType,
          status: 'interested',
          notes: notes.trim() || undefined,
        }),
      });
      setProposalSuccess(`Successfully recorded sponsorship commitment of ${formatCurrency(Number(amount), 'INR')}!`);
      setShowSponsorModal(false);
      setNotes('');
    } catch (err) {
      alert(err.message || 'Failed to submit commitment proposal.');
    } finally {
      setIsSubmittingProposal(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 36, height: 36 }} />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="section" style={{ minHeight: '60vh', display: 'flex', alignItems: 'center' }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: 24, marginBottom: 12 }}>Project Not Found</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
            {error || 'This showcase does not exist or has not been published.'}
          </p>
          <Link to="/projects">
            <Button variant="primary">Browse All Showcases</Button>
          </Link>
        </div>
      </div>
    );
  }

  const isOwner = user?.entrepreneur_profile && project.entrepreneur_id === user.entrepreneur_profile.id;
  const isSponsor = user?.role === 'sponsor';

  const currentAmount = project.current_funding || project.funding_received || 0;
  const targetAmount = project.funding_goal || 1;
  const progressPct = Math.min(100, Math.round((currentAmount / targetAmount) * 100));

  const displayImage = project.logo_url || project.cover_image_url;

  return (
    <div className="section" style={{ paddingTop: 32, paddingBottom: 80 }}>
      <div className="container" style={{ maxWidth: 1000 }}>
        {/* Navigation Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
          <Link to="/projects" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Showcases</Link>
          <span>/</span>
          <span style={{ color: 'var(--brand-cyan)' }}>{project.category}</span>
          <span>/</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{project.title}</span>
        </div>

        {proposalSuccess && (
          <div className="alert alert-success" style={{ marginBottom: 24 }}>
            <span>{proposalSuccess}</span>
          </div>
        )}

        {/* Owner Management Bar (if viewed by founder) */}
        {isOwner && (
          <div
            style={{
              padding: '12px 20px',
              backgroundColor: 'rgba(6, 182, 212, 0.1)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 12,
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 13, color: 'var(--brand-cyan)', fontWeight: 600 }}>Founder View</span>
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                You are previewing your showcase as seen by verified sponsors.
              </span>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link to={`/projects/${project.id}/edit`} style={{ textDecoration: 'none' }}>
                <Button variant="secondary" size="sm">
                  Edit Showcase
                </Button>
              </Link>
              <Link to="/dashboard/entrepreneur" style={{ textDecoration: 'none' }}>
                <Button variant="ghost" size="sm">
                  Dashboard
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* 1. Project Header */}
        <div
          className="card"
          style={{
            marginBottom: 28,
            padding: 32,
            border: '1px solid var(--border-subtle)',
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(6, 182, 212, 0.08) 100%)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 24, flexWrap: 'wrap' }}>
            {displayImage ? (
              <img
                src={displayImage}
                alt={project.title}
                style={{
                  width: 96,
                  height: 96,
                  borderRadius: 'var(--radius-lg)',
                  objectFit: 'cover',
                  border: '1px solid var(--border-subtle)',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  flexShrink: 0,
                }}
              />
            ) : (
              <div
                style={{
                  width: 96,
                  height: 96,
                  borderRadius: 'var(--radius-lg)',
                  background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(59, 130, 246, 0.25) 100%)',
                  border: '1px solid rgba(6, 182, 212, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 40,
                  flexShrink: 0,
                }}
              >
                💡
              </div>
            )}

            <div style={{ flex: 1, minWidth: 280 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 8 }}>
                <Badge variant="cyan">{project.category}</Badge>
                {project.industry && <Badge variant="slate">{project.industry}</Badge>}
                <Badge variant="indigo" style={{ textTransform: 'capitalize' }}>
                  {project.stage} stage
                </Badge>
                <Badge variant={project.status === 'funded' ? 'emerald' : project.status === 'draft' ? 'amber' : 'cyan'}>
                  {project.status.replace('_', ' ')}
                </Badge>
              </div>

              <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.02em' }}>
                {project.title}
              </h1>

              <p style={{ fontSize: 16, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 18 }}>
                {project.tagline}
              </p>

              {/* Meta details & External links */}
              <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 20, fontSize: 13, color: 'var(--text-muted)' }}>
                {project.location && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>📍</span>
                    <span>{project.location}</span>
                  </div>
                )}
                {project.timeline && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>⏱️</span>
                    <span>{project.timeline}</span>
                  </div>
                )}

                <div style={{ display: 'flex', gap: 14, marginLeft: 'auto' }}>
                  {project.website_url && (
                    <a
                      href={project.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--brand-cyan)', textDecoration: 'none', fontWeight: 600 }}
                    >
                      🔗 Demo / Website ↗
                    </a>
                  )}
                  {project.pitch_deck_url && (
                    <a
                      href={project.pitch_deck_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--brand-cyan)', textDecoration: 'none', fontWeight: 600 }}
                    >
                      📄 Pitch Deck ↗
                    </a>
                  )}
                  {project.video_url && (
                    <a
                      href={project.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--brand-emerald)', textDecoration: 'none', fontWeight: 600 }}
                    >
                      ▶ Video Showcase ↗
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid: Left content (Problem, Solution, etc.) + Right Sidebar (Funding, Founder, etc.) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, alignItems: 'start' }}>
          {/* Main Left Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, flex: 2 }}>
            {/* 2. Problem */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 18 }}>⚠️</span>
                <h3 style={{ fontSize: 18, fontWeight: 700 }}>The Problem</h3>
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
                {project.problem_statement || 'Problem statement details available upon request.'}
              </p>
            </div>

            {/* 3. Solution */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 18 }}>💡</span>
                <h3 style={{ fontSize: 18, fontWeight: 700 }}>Proposed Innovative Solution</h3>
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
                {project.proposed_solution || 'Proposed technical architecture details available upon request.'}
              </p>
            </div>

            {/* 4. About the Startup */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 14 }}>About the Startup</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 20, whiteSpace: 'pre-line' }}>
                {project.description}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                <div>
                  <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 6 }}>
                    Target Users & Market
                  </h4>
                  <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {project.target_market || 'Specific industry operators and end-users.'}
                  </p>
                </div>
                <div>
                  <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 6 }}>
                    Unique Value Proposition
                  </h4>
                  <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {project.value_proposition || 'Proprietary efficiency and performance gains.'}
                  </p>
                </div>
              </div>
            </div>

            {/* 5. Technology / Skills */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Technology & Skills Needed</h3>

              <div style={{ marginBottom: 18 }}>
                <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 10 }}>
                  Technology / Tech Stack
                </h4>
                {(project.tech_stack || []).length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {project.tech_stack.map((t) => (
                      <span
                        key={t}
                        style={{
                          padding: '6px 12px',
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'rgba(6, 182, 212, 0.12)',
                          border: '1px solid rgba(6, 182, 212, 0.25)',
                          color: 'var(--brand-cyan)',
                          fontSize: 13,
                          fontWeight: 600,
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Tech stack specifications available on request.</p>
                )}
              </div>

              <div>
                <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 10 }}>
                  Skills & Talent Needed
                </h4>
                {(project.skills_needed || []).length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {project.skills_needed.map((s) => (
                      <span
                        key={s}
                        style={{
                          padding: '6px 12px',
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'rgba(16, 185, 129, 0.12)',
                          border: '1px solid rgba(16, 185, 129, 0.25)',
                          color: 'var(--brand-emerald)',
                          fontSize: 13,
                          fontWeight: 600,
                        }}
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Core founding team in place.</p>
                )}
              </div>
            </div>

            {/* 6. Current Progress */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Current Progress & Milestones</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
                {project.current_progress || 'Active development phase with initial validation benchmarks complete.'}
              </p>
            </div>

            {/* 9. Project Timeline */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Execution Timeline</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
                {project.timeline || 'Structured rollout plan with quarterly milestone tranches.'}
              </p>
            </div>
          </div>

          {/* Right Sidebar Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, flex: 1 }}>
            {/* 7. Funding Goal & Progress */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Funding & Capital</h3>

              <div style={{ padding: 16, backgroundColor: 'rgba(7, 9, 14, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: 18 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 8 }}>
                  <span style={{ fontSize: 24, fontWeight: 800, color: 'var(--brand-emerald)' }}>
                    {formatCurrency(currentAmount, project.currency || 'INR')}
                  </span>
                  <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    of {formatCurrency(targetAmount, project.currency || 'INR')} goal
                  </span>
                </div>

                <div style={{ width: '100%', height: 8, backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden', marginBottom: 8 }}>
                  <div
                    style={{
                      width: `${progressPct}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, var(--brand-cyan) 0%, var(--brand-emerald) 100%)',
                      borderRadius: 4,
                    }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-secondary)' }}>
                  <span>{progressPct}% Funded</span>
                  <span>{project.commitments_count || 0} Sponsor Commitments</span>
                </div>
              </div>

              {/* 8. Required Support */}
              <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 10 }}>
                Required Sponsorship Support
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
                {(project.required_support || []).map((type) => (
                  <Badge key={type} variant="cyan">
                    {type}
                  </Badge>
                ))}
              </div>

              {project.required_resources && (
                <div style={{ padding: 12, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-md)', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
                  <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 4 }}>Specific Resources Needed:</strong>
                  {project.required_resources}
                </div>
              )}

              {/* 12. Sponsorship CTA */}
              <div style={{ paddingTop: 8 }}>
                {isOwner ? (
                  <Link to={`/projects/${project.id}/edit`} style={{ textDecoration: 'none' }}>
                    <Button variant="secondary" style={{ width: '100%' }}>
                      Edit Showcase Details
                    </Button>
                  </Link>
                ) : isSponsor ? (
                  <Button
                    variant="emerald"
                    size="lg"
                    style={{ width: '100%' }}
                    onClick={() => setShowSponsorModal(true)}
                  >
                    Initiate Sponsorship Interest →
                  </Button>
                ) : isAuthenticated ? (
                  <Button
                    variant="primary"
                    style={{ width: '100%' }}
                    onClick={() => setShowSponsorModal(true)}
                  >
                    Connect With Founder
                  </Button>
                ) : (
                  <Link to="/register" style={{ textDecoration: 'none' }}>
                    <Button variant="emerald" style={{ width: '100%' }}>
                      Sign Up as Sponsor to Back
                    </Button>
                  </Link>
                )}
              </div>
            </div>

            {/* 10. Founder Information */}
            {project.founder && (
              <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14 }}>Founder Information</h3>

                <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 14 }}>
                  {project.founder.avatar_url ? (
                    <img
                      src={project.founder.avatar_url}
                      alt={project.founder.full_name}
                      style={{ width: 52, height: 52, borderRadius: '50%', objectFit: 'cover' }}
                    />
                  ) : (
                    <div
                      style={{
                        width: 52,
                        height: 52,
                        borderRadius: '50%',
                        backgroundColor: 'rgba(6, 182, 212, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 22,
                        color: 'var(--brand-cyan)',
                      }}
                    >
                      👤
                    </div>
                  )}

                  <div>
                    <h4 style={{ fontSize: 16, fontWeight: 700, marginBottom: 2 }}>
                      {project.founder.full_name}
                    </h4>
                    {project.founder.username && (
                      <div style={{ fontSize: 12, color: 'var(--brand-cyan)' }}>
                        @{project.founder.username}
                      </div>
                    )}
                    {project.founder.headline && (
                      <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                        {project.founder.headline}
                      </p>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', backgroundColor: 'rgba(7, 9, 14, 0.6)', borderRadius: 'var(--radius-md)', marginBottom: 14 }}>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Founder Trust Score</span>
                  <TrustScoreBadge score={project.founder.trust_score || 50} size="sm" />
                </div>

                {project.founder.username && (
                  <Link to={`/p/${project.founder.username}`} style={{ textDecoration: 'none' }}>
                    <Button variant="ghost" size="sm" style={{ width: '100%' }}>
                      View Full Founder Profile →
                    </Button>
                  </Link>
                )}
              </div>
            )}

            {/* 11. Project Verification / Trust */}
            <div className="card" style={{ border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 18 }}>🛡️</span>
                <h3 style={{ fontSize: 16, fontWeight: 700 }}>Verification & Trust</h3>
              </div>

              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                <p style={{ marginBottom: 10 }}>
                  This project showcase is verified on the Vynk cryptographic trust architecture. Milestones and commitments are audit-logged for accountability.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12, color: 'var(--text-muted)' }}>
                  <div>✓ Identity & profile verified</div>
                  <div>✓ Milestone-based tranche tracking enabled</div>
                  <div>✓ Mutual accountability protocol</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sponsor Commitment Modal */}
        {showSponsorModal && (
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
                <h3 style={{ fontSize: 20, fontWeight: 700 }}>Initiate Sponsorship Interest</h3>
                <button
                  onClick={() => setShowSponsorModal(false)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <div
                style={{
                  padding: 14,
                  backgroundColor: 'rgba(6, 182, 212, 0.08)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(6, 182, 212, 0.2)',
                  marginBottom: 20,
                }}
              >
                <div style={{ fontSize: 11, color: 'var(--brand-cyan)', fontWeight: 700 }}>TARGET VENTURE</div>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{project.title}</div>
              </div>

              <form onSubmit={handleProposeCommitment}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Proposed Allocation (₹)</label>
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
                    <label className="form-label">Support Vehicle</label>
                    <select
                      className="form-select"
                      value={sponsorshipType}
                      onChange={(e) => setSponsorshipType(e.target.value)}
                    >
                      <option value="grant">Non-Dilutive Grant</option>
                      <option value="equity">Equity Sponsorship</option>
                      <option value="convertible_note">Convertible Note</option>
                      <option value="credits">Cloud / Compute Credits</option>
                      <option value="mentorship">Strategic Mentorship</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Collaboration Notes & Introduction</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    placeholder="Introduce your organization and what support or synergies you propose..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                  <Button variant="ghost" onClick={() => setShowSponsorModal(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="emerald" isLoading={isSubmittingProposal}>
                    Propose Commitment
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
