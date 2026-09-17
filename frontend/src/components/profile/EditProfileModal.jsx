import React, { useState, useEffect } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { profileService } from '../../services/profileService';

// Default avatar presets for quick 1-click selection
const AVATAR_PRESETS = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&fit=crop&q=80',
];

const LOGO_PRESETS = [
  'https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&fit=crop&q=80',
  'https://images.unsplash.com/photo-1554774853-719586f82d77?w=400&fit=crop&q=80',
];

const COMMON_AREAS_SUPPORTED = [
  'Pre-Seed Capital',
  'Seed Investment',
  'Non-dilutive Grants',
  'Cloud Credits (AWS/GCP)',
  'AI Compute / GPUs',
  'GTM & Sales Mentorship',
  'Technical Architecture',
  'Laboratory & Foundry',
  'Office Space',
  'Legal & IP Counsel',
];

export function EditProfileModal({ profile, isOpen, onClose, onSaved }) {
  const isEntrepreneur = profile?.role === 'entrepreneur';
  const [activeTab, setActiveTab] = useState('identity');

  // Form states
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [headline, setHeadline] = useState('');
  const [bio, setBio] = useState('');
  const [location, setLocation] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');

  // Entrepreneur fields
  const [stage, setStage] = useState('idea');
  const [industry, setIndustry] = useState('');
  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState('');
  const [experience, setExperience] = useState([]);
  const [education, setEducation] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [pitchDeckUrl, setPitchDeckUrl] = useState('');

  // Sponsor fields
  const [orgName, setOrgName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [aboutOrg, setAboutOrg] = useState('');
  const [sponsorType, setSponsorType] = useState('individual_angel');
  const [minBudget, setMinBudget] = useState(5000);
  const [maxBudget, setMaxBudget] = useState(100000);
  const [focusIndustries, setFocusIndustries] = useState([]);
  const [focusInput, setFocusInput] = useState('');
  const [sponsorshipInterests, setSponsorshipInterests] = useState([]);
  const [interestInput, setInterestInput] = useState('');
  const [areasSupported, setAreasSupported] = useState([]);
  const [previousCollaborations, setPreviousCollaborations] = useState([]);

  // Item builder states for experience, education, achievements, collaborations
  const [expTitle, setExpTitle] = useState('');
  const [expCompany, setExpCompany] = useState('');
  const [expDuration, setExpDuration] = useState('');
  const [expDesc, setExpDesc] = useState('');

  const [eduInst, setEduInst] = useState('');
  const [eduDegree, setEduDegree] = useState('');
  const [eduYear, setEduYear] = useState('');

  const [achTitle, setAchTitle] = useState('');
  const [achYear, setAchYear] = useState('');
  const [achDesc, setAchDesc] = useState('');

  const [collabPartner, setCollabPartner] = useState('');
  const [collabYear, setCollabYear] = useState('');
  const [collabDesc, setCollabDesc] = useState('');
  const [collabOutcome, setCollabOutcome] = useState('');

  // Loading & error handling
  const [isSaving, setIsSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Hydrate initial values when modal opens
  useEffect(() => {
    if (!profile) return;
    setFullName(profile.full_name || '');
    setUsername(profile.username || '');
    setHeadline(profile.headline || '');
    setBio(profile.bio || '');
    setLocation(profile.location || '');
    setAvatarUrl(profile.avatar_url || '');

    if (profile.role === 'entrepreneur') {
      const ep = profile.entrepreneur_profile || {};
      setStage(ep.stage || 'idea');
      setIndustry(ep.industry || '');
      setSkills(Array.isArray(ep.skills) ? ep.skills : []);
      setExperience(Array.isArray(ep.experience) ? ep.experience : []);
      setEducation(Array.isArray(ep.education) ? ep.education : []);
      setAchievements(Array.isArray(ep.achievements) ? ep.achievements : []);
      setWebsiteUrl(ep.website_url || '');
      setLinkedinUrl(ep.linkedin_url || '');
      setGithubUrl(ep.github_url || '');
      setPitchDeckUrl(ep.pitch_deck_url || '');
    } else if (profile.role === 'sponsor') {
      const sp = profile.sponsor_profile || {};
      setOrgName(sp.organization_name || '');
      setLogoUrl(sp.logo_url || '');
      setAboutOrg(sp.about || profile.bio || '');
      setIndustry(sp.industry || '');
      setSponsorType(sp.sponsor_type || 'individual_angel');
      setMinBudget(sp.min_budget || 5000);
      setMaxBudget(sp.max_budget || 100000);
      setFocusIndustries(Array.isArray(sp.focus_industries) ? sp.focus_industries : []);
      setSponsorshipInterests(Array.isArray(sp.sponsorship_interests) ? sp.sponsorship_interests : []);
      setAreasSupported(Array.isArray(sp.areas_supported) ? sp.areas_supported : []);
      setPreviousCollaborations(Array.isArray(sp.previous_collaborations) ? sp.previous_collaborations : []);
    }
  }, [profile, isOpen]);

  if (!isOpen) return null;

  // Tag helper
  const addTag = (list, setList, input, setInput) => {
    const trimmed = input.trim();
    if (trimmed && !list.includes(trimmed)) {
      setList([...list, trimmed]);
      setInput('');
    }
  };

  const removeTag = (list, setList, index) => {
    setList(list.filter((_, i) => i !== index));
  };

  const toggleAreaSupported = (area) => {
    if (areasSupported.includes(area)) {
      setAreasSupported(areasSupported.filter((a) => a !== area));
    } else {
      setAreasSupported([...areasSupported, area]);
    }
  };

  // Add Item Helpers
  const addExperienceItem = () => {
    if (!expTitle.trim() || !expCompany.trim()) return;
    setExperience([
      ...experience,
      {
        title: expTitle.trim(),
        company: expCompany.trim(),
        duration: expDuration.trim() || 'Present',
        description: expDesc.trim(),
      },
    ]);
    setExpTitle('');
    setExpCompany('');
    setExpDuration('');
    setExpDesc('');
  };

  const addEducationItem = () => {
    if (!eduInst.trim() || !eduDegree.trim()) return;
    setEducation([
      ...education,
      {
        institution: eduInst.trim(),
        degree: eduDegree.trim(),
        year: eduYear.trim() || 'Graduated',
      },
    ]);
    setEduInst('');
    setEduDegree('');
    setEduYear('');
  };

  const addAchievementItem = () => {
    if (!achTitle.trim()) return;
    setAchievements([
      ...achievements,
      {
        title: achTitle.trim(),
        year: achYear.trim(),
        description: achDesc.trim(),
      },
    ]);
    setAchTitle('');
    setAchYear('');
    setAchDesc('');
  };

  const addCollaborationItem = () => {
    if (!collabPartner.trim()) return;
    setPreviousCollaborations([
      ...previousCollaborations,
      {
        partner_name: collabPartner.trim(),
        year: collabYear.trim(),
        description: collabDesc.trim(),
        outcome: collabOutcome.trim(),
      },
    ]);
    setCollabPartner('');
    setCollabYear('');
    setCollabDesc('');
    setCollabOutcome('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setErrorMsg('');
    setSuccessMsg('');

    // Validation
    if (!fullName.trim()) {
      setErrorMsg('Full name cannot be empty.');
      setIsSaving(false);
      return;
    }

    if (username.trim().length < 3) {
      setErrorMsg('Username must be at least 3 characters long.');
      setIsSaving(false);
      return;
    }

    const payload = {
      full_name: fullName.trim(),
      username: username.trim().toLowerCase(),
      headline: headline.trim() || null,
      bio: bio.trim() || null,
      location: location.trim() || null,
      avatar_url: avatarUrl.trim() || null,
    };

    if (isEntrepreneur) {
      payload.stage = stage;
      payload.industry = industry.trim() || null;
      payload.skills = skills;
      payload.experience = experience;
      payload.education = education;
      payload.achievements = achievements;
      payload.website_url = websiteUrl.trim() || null;
      payload.linkedin_url = linkedinUrl.trim() || null;
      payload.github_url = githubUrl.trim() || null;
      payload.pitch_deck_url = pitchDeckUrl.trim() || null;
    } else {
      payload.organization_name = orgName.trim() || null;
      payload.logo_url = logoUrl.trim() || null;
      payload.about = aboutOrg.trim() || null;
      payload.industry = industry.trim() || null;
      payload.sponsor_type = sponsorType;
      payload.min_budget = Number(minBudget);
      payload.max_budget = Number(maxBudget);
      payload.focus_industries = focusIndustries;
      payload.sponsorship_interests = sponsorshipInterests;
      payload.areas_supported = areasSupported;
      payload.previous_collaborations = previousCollaborations;
    }

    try {
      const updated = await profileService.updateMyProfile(payload);
      setSuccessMsg('Profile updated successfully!');
      setTimeout(() => {
        if (onSaved) onSaved(updated);
        onClose();
      }, 600);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 999,
        backgroundColor: 'rgba(7, 9, 14, 0.85)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: 780,
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          padding: 0,
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(6, 182, 212, 0.15)',
          border: '1px solid var(--border-medium)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(6, 182, 212, 0.08) 100%)',
          }}
        >
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
              Edit Professional Profile
            </h2>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
              Keep your credentials up to date to maximize match relevance.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: 22,
              cursor: 'pointer',
              padding: 4,
            }}
          >
            ✕
          </button>
        </div>

        {/* Modal Tabs */}
        <div
          style={{
            display: 'flex',
            gap: 8,
            padding: '10px 20px',
            borderBottom: '1px solid var(--border-subtle)',
            background: 'rgba(10, 14, 22, 0.7)',
            overflowX: 'auto',
          }}
        >
          <button
            type="button"
            className={`btn btn-sm ${activeTab === 'identity' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('identity')}
          >
            1. Identity
          </button>
          <button
            type="button"
            className={`btn btn-sm ${activeTab === 'overview' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('overview')}
          >
            2. Overview & Bio
          </button>
          <button
            type="button"
            className={`btn btn-sm ${activeTab === 'skills' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('skills')}
          >
            {isEntrepreneur ? '3. Skills' : '3. Interests & Support'}
          </button>
          <button
            type="button"
            className={`btn btn-sm ${activeTab === 'timeline' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('timeline')}
          >
            {isEntrepreneur ? '4. Experience & Edu' : '4. Collaborations'}
          </button>
          {isEntrepreneur && (
            <button
              type="button"
              className={`btn btn-sm ${activeTab === 'links' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('links')}
            >
              5. Web & Pitch Links
            </button>
          )}
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
          <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
            {errorMsg && (
              <div
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#F87171',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: 13,
                  marginBottom: 16,
                }}
              >
                {errorMsg}
              </div>
            )}
            {successMsg && (
              <div
                style={{
                  backgroundColor: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: 'var(--brand-emerald)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: 13,
                  marginBottom: 16,
                }}
              >
                {successMsg}
              </div>
            )}

            {/* TAB 1: IDENTITY */}
            {activeTab === 'identity' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                {/* Avatar Preview & Chooser */}
                <div>
                  <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
                    {isEntrepreneur ? 'Profile Photo / Avatar' : 'Representative Photo & Organization Logo'}
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                    <div
                      style={{
                        width: 72,
                        height: 72,
                        borderRadius: '50%',
                        backgroundColor: 'var(--bg-card-hover)',
                        overflow: 'hidden',
                        border: '2px solid var(--brand-cyan)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      {avatarUrl ? (
                        <img src={avatarUrl} alt="Avatar Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      ) : (
                        <span style={{ fontSize: 24, color: 'var(--text-muted)' }}>👤</span>
                      )}
                    </div>
                    <div style={{ flex: 1, minWidth: 240 }}>
                      <Input
                        label="Avatar Image URL"
                        placeholder="https://example.com/avatar.jpg"
                        value={avatarUrl}
                        onChange={(e) => setAvatarUrl(e.target.value)}
                      />
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Presets:</span>
                        {AVATAR_PRESETS.slice(0, 4).map((pUrl, i) => (
                          <img
                            key={i}
                            src={pUrl}
                            alt={`Preset ${i}`}
                            onClick={() => setAvatarUrl(pUrl)}
                            style={{
                              width: 24,
                              height: 24,
                              borderRadius: '50%',
                              cursor: 'pointer',
                              border: avatarUrl === pUrl ? '2px solid var(--brand-cyan)' : '1px solid var(--border-subtle)',
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {!isEntrepreneur && (
                  <div>
                    <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
                      Company / Organization Logo
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                      <div
                        style={{
                          width: 72,
                          height: 72,
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'var(--bg-card-hover)',
                          overflow: 'hidden',
                          border: '2px solid var(--brand-emerald)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                        }}
                      >
                        {logoUrl ? (
                          <img src={logoUrl} alt="Logo Preview" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                        ) : (
                          <span style={{ fontSize: 24, color: 'var(--text-muted)' }}>🏢</span>
                        )}
                      </div>
                      <div style={{ flex: 1, minWidth: 240 }}>
                        <Input
                          label="Organization Logo URL"
                          placeholder="https://example.com/logo.png"
                          value={logoUrl}
                          onChange={(e) => setLogoUrl(e.target.value)}
                        />
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
                          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Presets:</span>
                          {LOGO_PRESETS.map((pUrl, i) => (
                            <img
                              key={i}
                              src={pUrl}
                              alt={`Preset Logo ${i}`}
                              onClick={() => setLogoUrl(pUrl)}
                              style={{
                                width: 24,
                                height: 24,
                                borderRadius: 4,
                                cursor: 'pointer',
                                border: logoUrl === pUrl ? '2px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <Input
                    label="Full Name *"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Elena Rostova"
                    required
                  />

                  <div>
                    <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 6 }}>
                      Username *
                    </label>
                    <div style={{ position: 'relative' }}>
                      <span
                        style={{
                          position: 'absolute',
                          left: 12,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          color: 'var(--brand-cyan)',
                          fontWeight: 700,
                        }}
                      >
                        @
                      </span>
                      <input
                        type="text"
                        className="input"
                        style={{ paddingLeft: 28 }}
                        value={username}
                        onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                        placeholder="username"
                        required
                        maxLength={30}
                      />
                    </div>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                      Letters, numbers, underscores (3-30 chars).
                    </span>
                  </div>
                </div>

                {!isEntrepreneur && (
                  <Input
                    label="Company / Fund / Organization Name"
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    placeholder="e.g. Horizon Frontier Ventures"
                  />
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <Input
                    label="Professional Headline"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    placeholder={isEntrepreneur ? 'e.g. Founder & CEO @ DeepMind Robotics' : 'e.g. Managing Partner @ CleanTech Capital'}
                  />
                  <Input
                    label="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. San Francisco, CA · Remote"
                  />
                </div>
              </div>
            )}

            {/* TAB 2: OVERVIEW & BIO */}
            {activeTab === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    {isEntrepreneur ? 'Short Bio & Founder Vision' : 'About Organization & Investment Philosophy'}
                  </label>
                  <textarea
                    className="input"
                    rows={5}
                    value={isEntrepreneur ? bio : aboutOrg}
                    onChange={(e) => (isEntrepreneur ? setBio(e.target.value) : setAboutOrg(e.target.value))}
                    placeholder={
                      isEntrepreneur
                        ? 'Share your background, what motivated you to build this venture, and what problems you are solving...'
                        : 'Describe your organization, mission, sectors of interest, and what type of support or grants you provide...'
                    }
                    style={{ resize: 'vertical', minHeight: 120 }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  {isEntrepreneur ? (
                    <>
                      <div>
                        <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 6 }}>
                          Startup Stage
                        </label>
                        <select className="input" value={stage} onChange={(e) => setStage(e.target.value)}>
                          <option value="idea">Idea Stage</option>
                          <option value="prototype">Prototype / Working Demo</option>
                          <option value="mvp">MVP (Minimum Viable Product)</option>
                          <option value="launched">Launched / Live Traction</option>
                          <option value="scaling">Scaling / Early Revenue</option>
                        </select>
                      </div>

                      <Input
                        label="Primary Industry"
                        value={industry}
                        onChange={(e) => setIndustry(e.target.value)}
                        placeholder="e.g. AI/DeepTech, FinTech, HealthTech, CleanTech"
                      />
                    </>
                  ) : (
                    <>
                      <div>
                        <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 6 }}>
                          Sponsor Classification
                        </label>
                        <select className="input" value={sponsorType} onChange={(e) => setSponsorType(e.target.value)}>
                          <option value="individual_angel">Individual Angel Investor</option>
                          <option value="venture_capital">Venture Capital Fund</option>
                          <option value="corporate_accelerator">Corporate Accelerator / Lab</option>
                          <option value="grant_foundation">Grant Foundation / Non-Profit</option>
                          <option value="angel_network">Angel Syndicate / Network</option>
                        </select>
                      </div>

                      <Input
                        label="Primary Sector Focus"
                        value={industry}
                        onChange={(e) => setIndustry(e.target.value)}
                        placeholder="e.g. DeepTech & Climate, B2B SaaS, Health"
                      />
                    </>
                  )}
                </div>

                {!isEntrepreneur && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <Input
                      label="Minimum Sponsorship Budget ($)"
                      type="number"
                      value={minBudget}
                      onChange={(e) => setMinBudget(e.target.value)}
                    />
                    <Input
                      label="Maximum Sponsorship Budget ($)"
                      type="number"
                      value={maxBudget}
                      onChange={(e) => setMaxBudget(e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: SKILLS / INTERESTS & SUPPORT */}
            {activeTab === 'skills' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                {isEntrepreneur ? (
                  <div>
                    <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                      Key Skills & Technologies (Press Enter or click Add)
                    </label>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                      <input
                        type="text"
                        className="input"
                        placeholder="e.g. PyTorch, Rust, Hardware Prototyping, B2B Sales"
                        value={skillInput}
                        onChange={(e) => setSkillInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addTag(skills, setSkills, skillInput, setSkillInput);
                          }
                        }}
                      />
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => addTag(skills, setSkills, skillInput, setSkillInput)}
                      >
                        Add Skill
                      </Button>
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {skills.map((skill, idx) => (
                        <span
                          key={idx}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6,
                            padding: '4px 10px',
                            borderRadius: 999,
                            backgroundColor: 'rgba(6, 182, 212, 0.12)',
                            color: 'var(--brand-cyan)',
                            fontSize: 13,
                            fontWeight: 500,
                            border: '1px solid rgba(6, 182, 212, 0.3)',
                          }}
                        >
                          {skill}
                          <span
                            onClick={() => removeTag(skills, setSkills, idx)}
                            style={{ cursor: 'pointer', fontSize: 14, opacity: 0.7 }}
                          >
                            ✕
                          </span>
                        </span>
                      ))}
                      {skills.length === 0 && (
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No skills added yet.</span>
                      )}
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Sponsor Interests */}
                    <div>
                      <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                        Sponsorship Interests & Stage Targets (Press Enter or click Add)
                      </label>
                      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                        <input
                          type="text"
                          className="input"
                          placeholder="e.g. Pre-Seed, Hardware Prototypes, AI Agents"
                          value={interestInput}
                          onChange={(e) => setInterestInput(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              addTag(sponsorshipInterests, setSponsorshipInterests, interestInput, setInterestInput);
                            }
                          }}
                        />
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={() => addTag(sponsorshipInterests, setSponsorshipInterests, interestInput, setInterestInput)}
                        >
                          Add
                        </Button>
                      </div>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 18 }}>
                        {sponsorshipInterests.map((interest, idx) => (
                          <span
                            key={idx}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 6,
                              padding: '4px 10px',
                              borderRadius: 999,
                              backgroundColor: 'rgba(16, 185, 129, 0.12)',
                              color: 'var(--brand-emerald)',
                              fontSize: 13,
                              fontWeight: 500,
                              border: '1px solid rgba(16, 185, 129, 0.3)',
                            }}
                          >
                            {interest}
                            <span
                              onClick={() => removeTag(sponsorshipInterests, setSponsorshipInterests, idx)}
                              style={{ cursor: 'pointer', fontSize: 14, opacity: 0.7 }}
                            >
                              ✕
                            </span>
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Areas Supported Checkboxes */}
                    <div>
                      <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
                        Areas Supported (Select all that apply)
                      </label>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
                        {COMMON_AREAS_SUPPORTED.map((area, idx) => {
                          const isSelected = areasSupported.includes(area);
                          return (
                            <div
                              key={idx}
                              onClick={() => toggleAreaSupported(area)}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 10,
                                padding: '8px 12px',
                                borderRadius: 'var(--radius-sm)',
                                background: isSelected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                                border: isSelected ? '1px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                              }}
                            >
                              <span style={{ color: isSelected ? 'var(--brand-emerald)' : 'var(--text-muted)' }}>
                                {isSelected ? '☑' : '☐'}
                              </span>
                              <span style={{ fontSize: 13, color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                                {area}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* TAB 4: EXPERIENCE & EDUCATION (or Collaborations) */}
            {activeTab === 'timeline' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {isEntrepreneur ? (
                  <>
                    {/* Experience Section */}
                    <div>
                      <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 10 }}>
                        Work Experience
                      </h4>
                      {experience.map((item, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: 12,
                            borderRadius: 'var(--radius-sm)',
                            background: 'rgba(255, 255, 255, 0.03)',
                            marginBottom: 8,
                            display: 'flex',
                            justifyContent: 'space-between',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, fontSize: 14 }}>{item.title} · <span style={{ color: 'var(--text-secondary)' }}>{item.company}</span></div>
                            <div style={{ fontSize: 12, color: 'var(--brand-cyan)' }}>{item.duration}</div>
                            {item.description && <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{item.description}</div>}
                          </div>
                          <button
                            type="button"
                            onClick={() => setExperience(experience.filter((_, i) => i !== idx))}
                            style={{ background: 'none', border: 'none', color: '#EF4444', cursor: 'pointer' }}
                          >
                            ✕
                          </button>
                        </div>
                      ))}

                      {/* Add experience inputs */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 8 }}>
                        <input
                          type="text"
                          className="input"
                          placeholder="Position / Title"
                          value={expTitle}
                          onChange={(e) => setExpTitle(e.target.value)}
                        />
                        <input
                          type="text"
                          className="input"
                          placeholder="Company / Venture"
                          value={expCompany}
                          onChange={(e) => setExpCompany(e.target.value)}
                        />
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10, marginTop: 8 }}>
                        <input
                          type="text"
                          className="input"
                          placeholder="Duration (e.g. 2021 - Present)"
                          value={expDuration}
                          onChange={(e) => setExpDuration(e.target.value)}
                        />
                        <input
                          type="text"
                          className="input"
                          placeholder="Key responsibilities or breakthroughs"
                          value={expDesc}
                          onChange={(e) => setExpDesc(e.target.value)}
                        />
                      </div>
                      <Button type="button" variant="secondary" size="sm" onClick={addExperienceItem} style={{ marginTop: 8 }}>
                        + Add Position
                      </Button>
                    </div>

                    {/* Education Section */}
                    <div style={{ paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                      <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 10 }}>
                        Education & Credentials
                      </h4>
                      {education.map((item, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: 12,
                            borderRadius: 'var(--radius-sm)',
                            background: 'rgba(255, 255, 255, 0.03)',
                            marginBottom: 8,
                            display: 'flex',
                            justifyContent: 'space-between',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, fontSize: 14 }}>{item.degree}</div>
                            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item.institution} ({item.year})</div>
                          </div>
                          <button
                            type="button"
                            onClick={() => setEducation(education.filter((_, i) => i !== idx))}
                            style={{ background: 'none', border: 'none', color: '#EF4444', cursor: 'pointer' }}
                          >
                            ✕
                          </button>
                        </div>
                      ))}

                      <div style={{ display: 'grid', gridTemplateColumns: '2fr 2fr 1fr', gap: 10, marginTop: 8 }}>
                        <input
                          type="text"
                          className="input"
                          placeholder="Degree / Certificate"
                          value={eduDegree}
                          onChange={(e) => setEduDegree(e.target.value)}
                        />
                        <input
                          type="text"
                          className="input"
                          placeholder="Institution / University"
                          value={eduInst}
                          onChange={(e) => setEduInst(e.target.value)}
                        />
                        <input
                          type="text"
                          className="input"
                          placeholder="Year"
                          value={eduYear}
                          onChange={(e) => setEduYear(e.target.value)}
                        />
                      </div>
                      <Button type="button" variant="secondary" size="sm" onClick={addEducationItem} style={{ marginTop: 8 }}>
                        + Add Education
                      </Button>
                    </div>

                    {/* Achievements Section */}
                    <div style={{ paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                      <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-cyan)', marginBottom: 10 }}>
                        Achievements, Grants & Awards
                      </h4>
                      {achievements.map((item, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: 12,
                            borderRadius: 'var(--radius-sm)',
                            background: 'rgba(255, 255, 255, 0.03)',
                            marginBottom: 8,
                            display: 'flex',
                            justifyContent: 'space-between',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, fontSize: 14 }}>{item.title} {item.year && `(${item.year})`}</div>
                            {item.description && <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{item.description}</div>}
                          </div>
                          <button
                            type="button"
                            onClick={() => setAchievements(achievements.filter((_, i) => i !== idx))}
                            style={{ background: 'none', border: 'none', color: '#EF4444', cursor: 'pointer' }}
                          >
                            ✕
                          </button>
                        </div>
                      ))}

                      <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: 10, marginTop: 8 }}>
                        <input
                          type="text"
                          className="input"
                          placeholder="Award / Grant / Patent Title"
                          value={achTitle}
                          onChange={(e) => setAchTitle(e.target.value)}
                        />
                        <input
                          type="text"
                          className="input"
                          placeholder="Year"
                          value={achYear}
                          onChange={(e) => setAchYear(e.target.value)}
                        />
                      </div>
                      <input
                        type="text"
                        className="input"
                        placeholder="Brief description or granting body"
                        value={achDesc}
                        onChange={(e) => setAchDesc(e.target.value)}
                        style={{ marginTop: 8 }}
                      />
                      <Button type="button" variant="secondary" size="sm" onClick={addAchievementItem} style={{ marginTop: 8 }}>
                        + Add Achievement
                      </Button>
                    </div>
                  </>
                ) : (
                  /* Previous Collaborations Section for Sponsors */
                  <div>
                    <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--brand-emerald)', marginBottom: 10 }}>
                      Previous Collaborations & Backed Ventures
                    </h4>
                    {previousCollaborations.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: 12,
                          borderRadius: 'var(--radius-sm)',
                          background: 'rgba(255, 255, 255, 0.03)',
                          marginBottom: 8,
                          display: 'flex',
                          justifyContent: 'space-between',
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14 }}>
                            {item.partner_name} {item.year && `(${item.year})`}
                          </div>
                          {item.description && (
                            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>{item.description}</div>
                          )}
                          {item.outcome && (
                            <div style={{ fontSize: 12, color: 'var(--brand-emerald)', marginTop: 4 }}>
                              Outcome: {item.outcome}
                            </div>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => setPreviousCollaborations(previousCollaborations.filter((_, i) => i !== idx))}
                          style={{ background: 'none', border: 'none', color: '#EF4444', cursor: 'pointer' }}
                        >
                          ✕
                        </button>
                      </div>
                    ))}

                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: 10, marginTop: 8 }}>
                      <input
                        type="text"
                        className="input"
                        placeholder="Partner Startup or Venture Name"
                        value={collabPartner}
                        onChange={(e) => setCollabPartner(e.target.value)}
                      />
                      <input
                        type="text"
                        className="input"
                        placeholder="Year"
                        value={collabYear}
                        onChange={(e) => setCollabYear(e.target.value)}
                      />
                    </div>
                    <input
                      type="text"
                      className="input"
                      placeholder="Nature of sponsorship provided (e.g. $50k grant & GPU access)"
                      value={collabDesc}
                      onChange={(e) => setCollabDesc(e.target.value)}
                      style={{ marginTop: 8 }}
                    />
                    <input
                      type="text"
                      className="input"
                      placeholder="Key outcome (e.g. Prototype validated, Series A closed)"
                      value={collabOutcome}
                      onChange={(e) => setCollabOutcome(e.target.value)}
                      style={{ marginTop: 8 }}
                    />
                    <Button type="button" variant="secondary" size="sm" onClick={addCollaborationItem} style={{ marginTop: 8 }}>
                      + Add Collaboration
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* TAB 5: LINKS & PITCH DECK (Entrepreneur) */}
            {activeTab === 'links' && isEntrepreneur && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Input
                  label="Official Website URL"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="https://yourstartup.com"
                />
                <Input
                  label="LinkedIn Profile URL"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                />
                <Input
                  label="GitHub / Code Repository URL"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username"
                />
                <Input
                  label="Pitch Deck Document Link"
                  value={pitchDeckUrl}
                  onChange={(e) => setPitchDeckUrl(e.target.value)}
                  placeholder="https://docsend.com/view/... or PDF drive link"
                />
              </div>
            )}
          </div>

          {/* Modal Footer */}
          <div
            style={{
              padding: '16px 24px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'rgba(10, 14, 22, 0.95)',
            }}
          >
            <Button type="button" variant="ghost" onClick={onClose} disabled={isSaving}>
              Cancel
            </Button>
            <div style={{ display: 'flex', gap: 12 }}>
              <Button type="submit" variant="primary" disabled={isSaving}>
                {isSaving ? 'Saving Changes...' : 'Save Profile Changes'}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
