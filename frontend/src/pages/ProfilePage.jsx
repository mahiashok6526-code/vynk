import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { profileService } from '../services/profileService';
import { TrustScoreBadge } from '../components/common/TrustScoreBadge';
import { TrustScoreBreakdownModal } from '../components/trust/TrustScoreBreakdownModal';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { VynkLogo } from '../components/common/VynkLogo';
import { ProfileCompletionCard } from '../components/profile/ProfileCompletionCard';
import { EditProfileModal } from '../components/profile/EditProfileModal';
import { formatCurrency } from '../utils/currency';

export function ProfilePage() {
  const { identifier } = useParams();
  const { user: currentUser } = useAuth();

  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isTrustModalOpen, setIsTrustModalOpen] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const loadProfile = async () => {
    setIsLoading(true);
    setError(null);
    try {
      let data;
      if (!identifier || identifier === 'me') {
        // Load authenticated profile
        data = await profileService.getMyProfile();
      } else {
        // Load public profile
        data = await profileService.getPublicProfile(identifier);
      }
      setProfile(data);
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError(err.message || 'Profile not found or unavailable.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [identifier]);

  const handleCopyLink = () => {
    const url = `${window.location.origin}/p/${profile?.username || profile?.id}`;
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 36, height: 36 }} />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="section" style={{ textAlign: 'center', paddingTop: 80, minHeight: '60vh' }}>
        <div className="container" style={{ maxWidth: 500 }}>
          <div style={{ marginBottom: 20 }}>
            <VynkLogo variant="symbol" size={48} />
          </div>
          <h2 style={{ fontSize: 26, marginBottom: 12, color: 'var(--text-primary)' }}>Profile Unavailable</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
            {error || 'The requested member profile does not exist or may have changed.'}
          </p>
          <Link to="/">
            <Button variant="primary">Return to Vynk Explore</Button>
          </Link>
        </div>
      </div>
    );
  }

  const isOwnProfile = profile.is_own_profile || (currentUser && currentUser.id === profile.id);
  const isEntrepreneur = profile.role === 'entrepreneur';
  const ep = profile.entrepreneur_profile || {};
  const sp = profile.sponsor_profile || {};
  const ts = profile.trust_score || { score: 50 };

  return (
    <div className="section" style={{ paddingTop: 30, minHeight: '85vh', paddingBottom: 60 }}>
      <div className="container" style={{ maxWidth: 960 }}>
        {/* Own Profile Indicator & Share Bar */}
        {isOwnProfile && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12,
              padding: '12px 18px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.2)',
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--brand-cyan)' }}>
              <span>👁</span>
              <span>This is your official Vynk public profile view as seen by {isEntrepreneur ? 'sponsors' : 'founders'}.</span>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={handleCopyLink}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: 12, color: 'var(--text-primary)' }}
              >
                {copiedLink ? '✓ Copied Link' : '🔗 Copy Public URL'}
              </button>
              <Button variant="primary" size="sm" onClick={() => setIsEditModalOpen(true)}>
                ✏️ Edit Profile
              </Button>
            </div>
          </div>
        )}

        {/* 6. PROFILE COMPLETION PROGRESS BAR (Visible on own profile) */}
        {isOwnProfile && profile.completion && (
          <ProfileCompletionCard
            completion={profile.completion}
            onEditClick={() => setIsEditModalOpen(true)}
          />
        )}

        {/* 1. IDENTITY SECTION */}
        <div
          className="card"
          style={{
            marginBottom: 24,
            padding: '32px 28px',
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(10, 14, 22, 0.9) 100%)',
            border: '1px solid var(--border-medium)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Subtle background glow circle */}
          <div
            style={{
              position: 'absolute',
              top: -60,
              right: -60,
              width: 220,
              height: 220,
              borderRadius: '50%',
              background: isEntrepreneur ? 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)' : 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%)',
              pointerEvents: 'none',
            }}
          />

          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 24 }}>
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
              {/* Profile Avatar / Logo */}
              <div
                style={{
                  width: 104,
                  height: 104,
                  borderRadius: isEntrepreneur ? '50%' : 'var(--radius-lg)',
                  border: isEntrepreneur ? '3px solid var(--brand-cyan)' : '3px solid var(--brand-emerald)',
                  overflow: 'hidden',
                  backgroundColor: 'var(--bg-card-hover)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
                  flexShrink: 0,
                }}
              >
                {isEntrepreneur ? (
                  profile.avatar_url ? (
                    <img src={profile.avatar_url} alt={profile.full_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <span style={{ fontSize: 42, color: 'var(--text-muted)' }}>👤</span>
                  )
                ) : (
                  sp.logo_url || profile.avatar_url ? (
                    <img src={sp.logo_url || profile.avatar_url} alt={sp.organization_name || profile.full_name} style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 8 }} />
                  ) : (
                    <span style={{ fontSize: 42, color: 'var(--text-muted)' }}>🏢</span>
                  )
                )}
              </div>

              {/* Identity Details */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 6 }}>
                  <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                    {!isEntrepreneur && sp.organization_name ? sp.organization_name : profile.full_name}
                  </h1>

                  {profile.username && (
                    <span style={{ fontSize: 16, color: 'var(--brand-cyan)', fontWeight: 600 }}>
                      @{profile.username}
                    </span>
                  )}

                  <Badge variant={isEntrepreneur ? 'cyan' : 'emerald'}>
                    {isEntrepreneur ? 'Founder' : sp.sponsor_type ? sp.sponsor_type.replace('_', ' ') : 'Sponsor'}
                  </Badge>

                  {profile.is_verified ? (
                    <Badge variant="emerald">✓ Verified Account</Badge>
                  ) : (
                    <Badge variant="amber">Community Member</Badge>
                  )}
                </div>

                {!isEntrepreneur && sp.organization_name && profile.full_name && (
                  <div style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Lead Representative: <strong style={{ color: 'var(--text-primary)' }}>{profile.full_name}</strong>
                  </div>
                )}

                {profile.headline && (
                  <p style={{ fontSize: 16, color: 'var(--text-secondary)', margin: '0 0 8px', fontWeight: 500 }}>
                    {profile.headline}
                  </p>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', fontSize: 13, color: 'var(--text-muted)' }}>
                  {profile.location && (
                    <span>📍 {profile.location}</span>
                  )}
                  <span>📅 Member since {new Date(profile.created_at).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}</span>
                </div>
              </div>
            </div>

            {/* Trust Score Card Preview */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 10 }}>
              <TrustScoreBadge
                score={ts.score ?? 50}
                size="lg"
                onClick={() => setIsTrustModalOpen(true)}
              />
              {isOwnProfile && (
                <Button variant="secondary" size="sm" onClick={() => setIsEditModalOpen(true)}>
                  Edit Profile
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* 2. ABOUT SECTION */}
        <div className="card" style={{ marginBottom: 24, padding: '24px 28px' }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 14, color: 'var(--brand-cyan)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📖</span> About
          </h3>
          <p style={{ fontSize: 15, lineHeight: 1.7, color: 'var(--text-secondary)', whiteSpace: 'pre-line', margin: 0 }}>
            {(isEntrepreneur ? profile.bio : sp.about || profile.bio) ||
              'No public bio provided yet. Keep your profile updated to give potential collaborators complete context.'}
          </p>

          {/* Quick Metrics Bar */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: 16,
              marginTop: 20,
              paddingTop: 18,
              borderTop: '1px solid var(--border-subtle)',
            }}
          >
            {isEntrepreneur ? (
              <>
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Startup Stage</div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-cyan)', marginTop: 2, textTransform: 'capitalize' }}>
                    {ep.stage || 'Idea Stage'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Primary Industry</div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                    {ep.industry || 'Tech / Innovation'}
                  </div>
                </div>
              </>
            ) : (
              <>
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Budget / Ticket Size</div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-emerald)', marginTop: 2 }}>
                    {formatCurrency(sp.min_budget || 5000, 'INR')} – {formatCurrency(sp.max_budget || 100000, 'INR')}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Sector Focus</div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                    {sp.industry || 'Cross-industry'}
                  </div>
                </div>
              </>
            )}

            {/* Social & Web Links */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              {ep.website_url && (
                <a href={ep.website_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ padding: '4px 10px' }}>
                  🌐 Website
                </a>
              )}
              {ep.linkedin_url && (
                <a href={ep.linkedin_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ padding: '4px 10px' }}>
                  💼 LinkedIn
                </a>
              )}
              {ep.github_url && (
                <a href={ep.github_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ padding: '4px 10px' }}>
                  💻 GitHub
                </a>
              )}
              {ep.pitch_deck_url && (
                <a href={ep.pitch_deck_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ padding: '4px 10px', color: 'var(--brand-cyan)' }}>
                  📊 Pitch Deck
                </a>
              )}
            </div>
          </div>
        </div>

        {/* 3. SKILLS / INTERESTS SECTION */}
        <div className="card" style={{ marginBottom: 24, padding: '24px 28px' }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 14, color: isEntrepreneur ? 'var(--brand-cyan)' : 'var(--brand-emerald)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>⚡</span> {isEntrepreneur ? 'Skills & Capabilities' : 'Sponsorship Interests & Areas Supported'}
          </h3>

          {isEntrepreneur ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {ep.skills && ep.skills.length > 0 ? (
                ep.skills.map((skill, idx) => (
                  <span
                    key={idx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '6px 14px',
                      borderRadius: 999,
                      backgroundColor: 'rgba(6, 182, 212, 0.1)',
                      color: 'var(--brand-cyan)',
                      fontSize: 13,
                      fontWeight: 600,
                      border: '1px solid rgba(6, 182, 212, 0.25)',
                    }}
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>No skills listed yet.</span>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase' }}>
                  Target Interests
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {sp.sponsorship_interests && sp.sponsorship_interests.length > 0 ? (
                    sp.sponsorship_interests.map((interest, idx) => (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          padding: '6px 14px',
                          borderRadius: 999,
                          backgroundColor: 'rgba(16, 185, 129, 0.1)',
                          color: 'var(--brand-emerald)',
                          fontSize: 13,
                          fontWeight: 600,
                          border: '1px solid rgba(16, 185, 129, 0.25)',
                        }}
                      >
                        {interest}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No specific target interests listed.</span>
                  )}
                </div>
              </div>

              <div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase' }}>
                  Areas Supported
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {sp.areas_supported && sp.areas_supported.length > 0 ? (
                    sp.areas_supported.map((area, idx) => (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6,
                          padding: '6px 14px',
                          borderRadius: 999,
                          backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          color: '#A5B4FC',
                          fontSize: 13,
                          fontWeight: 600,
                          border: '1px solid rgba(99, 102, 241, 0.25)',
                        }}
                      >
                        ✓ {area}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Financial grants, mentorship, and cloud credits.</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 4. EXPERIENCE & ACHIEVEMENTS SECTION (or Collaborations) */}
        <div className="card" style={{ marginBottom: 24, padding: '24px 28px' }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 18, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>💼</span> {isEntrepreneur ? 'Experience & Background' : 'Previous Collaborations & Backed Ventures'}
          </h3>

          {isEntrepreneur ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* Experience list */}
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Work History
                </div>
                {ep.experience && ep.experience.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {ep.experience.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: 16,
                          borderRadius: 'var(--radius-md)',
                          background: 'rgba(255, 255, 255, 0.02)',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                            {item.title} · <span style={{ color: 'var(--brand-cyan)', fontWeight: 500 }}>{item.company}</span>
                          </div>
                          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{item.duration}</span>
                        </div>
                        {item.description && (
                          <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '8px 0 0', lineHeight: 1.6 }}>
                            {item.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>No prior work history listed.</span>
                )}
              </div>

              {/* Education list */}
              <div style={{ paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Education & Credentials
                </div>
                {ep.education && ep.education.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
                    {ep.education.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: 14,
                          borderRadius: 'var(--radius-md)',
                          background: 'rgba(255, 255, 255, 0.02)',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>{item.degree}</div>
                        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                          {item.institution} {item.year && `· ${item.year}`}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>No formal education credentials listed.</span>
                )}
              </div>

              {/* Achievements list */}
              {ep.achievements && ep.achievements.length > 0 && (
                <div style={{ paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Honors & Milestones
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {ep.achievements.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 12,
                          padding: 12,
                          borderRadius: 'var(--radius-md)',
                          background: 'rgba(245, 158, 11, 0.04)',
                          border: '1px solid rgba(245, 158, 11, 0.18)',
                        }}
                      >
                        <span style={{ fontSize: 18, color: 'var(--brand-amber)' }}>🏆</span>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                            {item.title} {item.year && `(${item.year})`}
                          </div>
                          {item.description && (
                            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>{item.description}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Sponsor Previous Collaborations */
            <div>
              {sp.previous_collaborations && sp.previous_collaborations.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {sp.previous_collaborations.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 16,
                        borderRadius: 'var(--radius-md)',
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                        <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                          {item.partner_name}
                        </div>
                        {item.year && <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{item.year}</span>}
                      </div>
                      {item.description && (
                        <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '6px 0 0', lineHeight: 1.5 }}>
                          {item.description}
                        </p>
                      )}
                      {item.outcome && (
                        <div style={{ fontSize: 13, color: 'var(--brand-emerald)', marginTop: 6, fontWeight: 500 }}>
                          🚀 Outcome: {item.outcome}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
                  No past sponsored collaborations listed yet.
                </span>
              )}
            </div>
          )}
        </div>

        {/* 5. PROJECTS / COLLABORATIONS SECTION */}
        {isEntrepreneur && (
          <div className="card" style={{ marginBottom: 24, padding: '24px 28px' }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🚀</span> Startups & Projects ({profile.projects?.length || 0})
            </h3>
            {profile.projects && profile.projects.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16 }}>
                {profile.projects.map((proj) => {
                  const pct = Math.min(100, Math.round(((proj.current_funding || 0) / (proj.funding_goal || 1)) * 100));
                  return (
                    <div
                      key={proj.id}
                      style={{
                        padding: 18,
                        borderRadius: 'var(--radius-md)',
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span style={{ fontSize: 12, color: 'var(--brand-cyan)', textTransform: 'uppercase', fontWeight: 600 }}>
                            {proj.category}
                          </span>
                          <Badge variant="cyan">{proj.stage}</Badge>
                        </div>
                        <h4 style={{ fontSize: 17, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-primary)' }}>
                          {proj.title}
                        </h4>
                        <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '0 0 14px', lineHeight: 1.5 }}>
                          {proj.tagline || proj.description}
                        </p>
                      </div>

                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                          <span style={{ color: 'var(--text-muted)' }}>Target: ${(proj.funding_goal || 0).toLocaleString()}</span>
                          <span style={{ color: 'var(--brand-emerald)', fontWeight: 600 }}>{pct}% Funded</span>
                        </div>
                        <div style={{ width: '100%', height: 6, backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: 999 }}>
                          <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--brand-emerald)', borderRadius: 999 }} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)' }}>
                <p style={{ margin: 0, fontSize: 14 }}>No active ventures published yet.</p>
                {isOwnProfile && (
                  <Link to="/dashboard/entrepreneur" style={{ marginTop: 10, display: 'inline-block' }}>
                    <Button variant="secondary" size="sm">+ Publish New Startup</Button>
                  </Link>
                )}
              </div>
            )}
          </div>
        )}

        {/* 6. VERIFICATION SECTION */}
        <div className="card" style={{ marginBottom: 24, padding: '24px 28px' }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12, color: 'var(--brand-emerald)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>🛡️</span> Platform Verification Status
          </h3>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 16,
              padding: 16,
              borderRadius: 'var(--radius-md)',
              background: profile.is_verified ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              border: `1px solid ${profile.is_verified ? 'rgba(16, 185, 129, 0.25)' : 'var(--border-subtle)'}`,
            }}
          >
            <div>
              <div style={{ fontSize: 15, fontWeight: 600, color: profile.is_verified ? 'var(--brand-emerald)' : 'var(--text-primary)' }}>
                {profile.is_verified ? '✓ Level 2 Identity & Accreditation Verified' : 'Level 1 Community Member (Pending Verification)'}
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                {profile.is_verified
                  ? 'This account has completed formal identity verification and institutional accreditation on Vynk.'
                  : 'Basic email confirmed. Enhanced verification unlocks premium investor discovery and elevated Trust Score.'}
              </div>
            </div>
            <Badge variant={profile.is_verified ? 'emerald' : 'amber'}>
              {profile.is_verified ? 'Accredited Member' : 'Standard'}
            </Badge>
          </div>
        </div>

        {/* 7. TRUST SCORE BREAKDOWN SECTION */}
        <div className="card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>💠</span> Vynk Verifiable Trust Score
              </h3>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                Auditable platform credibility derived from verified commitments, delivered milestones, and responsive communication.
              </p>
            </div>
            <TrustScoreBadge
              score={ts.score ?? 50}
              size="lg"
              onClick={() => setIsTrustModalOpen(true)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
            <div style={{ padding: 14, borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Verification Points</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--brand-cyan)', marginTop: 4 }}>
                {ts.verification_score ?? ts.verification_points ?? 0} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>/ 25</span>
              </div>
            </div>

            <div style={{ padding: 14, borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Commitment Reliability</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--brand-emerald)', marginTop: 4 }}>
                {ts.commitment_score ?? ts.commitments_points ?? 0} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>/ 35</span>
              </div>
            </div>

            <div style={{ padding: 14, borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Milestone Execution</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#A5B4FC', marginTop: 4 }}>
                {ts.milestone_score ?? 0} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>/ 20</span>
              </div>
            </div>

            <div style={{ padding: 14, borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Platform Responsiveness</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--brand-amber)', marginTop: 4 }}>
                {ts.activity_score ?? ts.activity_points ?? 0} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>/ 20</span>
              </div>
            </div>
          </div>

          <Button
            size="sm"
            variant="secondary"
            onClick={() => setIsTrustModalOpen(true)}
            style={{ width: '100%', marginTop: 20 }}
          >
            View Auditable Reputation Breakdown & History →
          </Button>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {isOwnProfile && (
        <EditProfileModal
          profile={profile}
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSaved={(updated) => {
            setProfile(updated);
          }}
        />
      )}

      {/* Trust Score Breakdown Modal */}
      <TrustScoreBreakdownModal
        isOpen={isTrustModalOpen}
        onClose={() => setIsTrustModalOpen(false)}
        userId={profile?.id}
        isPublic={!isOwnProfile}
      />
    </div>
  );
}
