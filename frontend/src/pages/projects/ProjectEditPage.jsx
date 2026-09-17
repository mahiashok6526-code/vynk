import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';

const CATEGORIES = [
  'CleanTech',
  'AI & Robotics',
  'HealthTech',
  'FinTech',
  'DeepTech',
  'AgTech',
  'EdTech',
  'Cybersecurity',
  'Aerospace',
];

const STAGES = [
  { value: 'idea', label: 'Idea Stage (Conceptualizing)' },
  { value: 'prototype', label: 'Prototype (Functional Test Units)' },
  { value: 'mvp', label: 'MVP (Initial Pilots & Traction)' },
  { value: 'launched', label: 'Launched (Market Active)' },
  { value: 'scaling', label: 'Scaling (Commercial Expansion)' },
];

const SUPPORT_TYPES = [
  'Capital',
  'Compute Credits',
  'Mentorship',
  'Hardware',
  'Cloud Resources',
  'Partnerships',
  'Other',
];

export function ProjectEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [projectStatus, setProjectStatus] = useState('draft');

  // 1. Identity & Overview
  const [title, setTitle] = useState('');
  const [tagline, setTagline] = useState('');
  const [category, setCategory] = useState('CleanTech');
  const [industry, setIndustry] = useState('');
  const [stage, setStage] = useState('mvp');
  const [coverImageUrl, setCoverImageUrl] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [location, setLocation] = useState('');

  // 2. Problem & Solution
  const [problemStatement, setProblemStatement] = useState('');
  const [proposedSolution, setProposedSolution] = useState('');
  const [targetMarket, setTargetMarket] = useState('');
  const [valueProposition, setValueProposition] = useState('');
  const [description, setDescription] = useState('');

  // 3. Technical & Progress
  const [currentProgress, setCurrentProgress] = useState('');
  const [techStackInput, setTechStackInput] = useState('');
  const [techStack, setTechStack] = useState([]);
  const [skillsNeededInput, setSkillsNeededInput] = useState('');
  const [skillsNeeded, setSkillsNeeded] = useState([]);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [pitchDeckUrl, setPitchDeckUrl] = useState('');
  const [videoUrl, setVideoUrl] = useState('');

  // 4. Funding & Support
  const [fundingGoal, setFundingGoal] = useState(50000);
  const [fundingReceived, setFundingReceived] = useState(0);
  const [requiredSupport, setRequiredSupport] = useState([]);
  const [requiredResources, setRequiredResources] = useState('');
  const [timeline, setTimeline] = useState('');

  // UI State
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  useEffect(() => {
    async function loadProject() {
      try {
        const p = await apiRequest(`/projects/${id}`);
        // Verify ownership
        if (p.entrepreneur_id !== user?.entrepreneur_profile?.id) {
          setServerError('You do not have permission to edit this project.');
          setIsLoading(false);
          return;
        }

        setTitle(p.title || '');
        setTagline(p.tagline || '');
        setCategory(p.category || 'CleanTech');
        setIndustry(p.industry || '');
        setStage(p.stage || 'idea');
        setCoverImageUrl(p.cover_image_url || '');
        setLogoUrl(p.logo_url || '');
        setLocation(p.location || '');
        setProblemStatement(p.problem_statement || '');
        setProposedSolution(p.proposed_solution || '');
        setTargetMarket(p.target_market || '');
        setValueProposition(p.value_proposition || '');
        setDescription(p.description || '');
        setCurrentProgress(p.current_progress || '');
        setTechStack(p.tech_stack || []);
        setSkillsNeeded(p.skills_needed || []);
        setWebsiteUrl(p.website_url || p.demo_url || '');
        setPitchDeckUrl(p.pitch_deck_url || '');
        setVideoUrl(p.video_url || '');
        setFundingGoal(p.funding_goal || 0);
        setFundingReceived(p.funding_received || 0);
        setRequiredSupport(p.required_support || []);
        setRequiredResources(p.required_resources || '');
        setTimeline(p.timeline || '');
        setProjectStatus(p.status || 'published');
      } catch (err) {
        setServerError(err.message || 'Failed to load project.');
      } finally {
        setIsLoading(false);
      }
    }
    loadProject();
  }, [id, user]);

  const handleAddTech = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = techStackInput.trim().replace(/^,|,$/g, '');
      if (val && !techStack.includes(val)) {
        setTechStack([...techStack, val]);
        setTechStackInput('');
      }
    }
  };

  const handleRemoveTech = (item) => {
    setTechStack(techStack.filter((t) => t !== item));
  };

  const handleAddSkill = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = skillsNeededInput.trim().replace(/^,|,$/g, '');
      if (val && !skillsNeeded.includes(val)) {
        setSkillsNeeded([...skillsNeeded, val]);
        setSkillsNeededInput('');
      }
    }
  };

  const handleRemoveSkill = (item) => {
    setSkillsNeeded(skillsNeeded.filter((s) => s !== item));
  };

  const toggleSupportType = (type) => {
    if (requiredSupport.includes(type)) {
      setRequiredSupport(requiredSupport.filter((t) => t !== type));
    } else {
      setRequiredSupport([...requiredSupport, type]);
    }
  };

  const validateForm = (isPublishing) => {
    const newErrors = {};

    if (!title.trim() || title.trim().length < 2) {
      newErrors.title = 'Project title is required.';
    }

    if (isPublishing) {
      if (!tagline.trim() || tagline.trim().length < 5) {
        newErrors.tagline = 'A tagline is required (minimum 5 characters).';
      }
      if (!description.trim() || description.trim().length < 10) {
        newErrors.description = 'Detailed description is required.';
      }
      if (!problemStatement.trim() || problemStatement.trim().length < 10) {
        newErrors.problemStatement = 'Problem statement is required.';
      }
      if (!proposedSolution.trim() || proposedSolution.trim().length < 10) {
        newErrors.proposedSolution = 'Proposed solution is required.';
      }
      if (!targetMarket.trim() || targetMarket.trim().length < 5) {
        newErrors.targetMarket = 'Target users / market is required.';
      }
      if (!valueProposition.trim() || valueProposition.trim().length < 5) {
        newErrors.valueProposition = 'Unique value proposition is required.';
      }
      if (!fundingGoal || Number(fundingGoal) <= 0) {
        newErrors.fundingGoal = 'Funding goal must be greater than 0.';
      }
      if (!requiredSupport || requiredSupport.length === 0) {
        newErrors.requiredSupport = 'Select at least one required support type.';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleUpdate = async (publish = false) => {
    setServerError('');
    const willPublish = publish || projectStatus.toLowerCase() !== 'draft';
    const isValid = validateForm(willPublish);
    if (!isValid) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        title: title.trim(),
        tagline: tagline.trim(),
        description: description.trim(),
        category,
        industry: industry.trim() || undefined,
        stage,
        problem_statement: problemStatement.trim() || undefined,
        proposed_solution: proposedSolution.trim() || undefined,
        target_market: targetMarket.trim() || undefined,
        value_proposition: valueProposition.trim() || undefined,
        current_progress: currentProgress.trim() || undefined,
        funding_goal: Number(fundingGoal) || 0,
        funding_received: Number(fundingReceived) || 0,
        required_support: requiredSupport,
        required_resources: requiredResources.trim() || undefined,
        skills_needed: skillsNeeded,
        tech_stack: techStack,
        website_url: websiteUrl.trim() || undefined,
        demo_url: websiteUrl.trim() || undefined,
        pitch_deck_url: pitchDeckUrl.trim() || undefined,
        video_url: videoUrl.trim() || undefined,
        cover_image_url: coverImageUrl.trim() || undefined,
        logo_url: logoUrl.trim() || coverImageUrl.trim() || undefined,
        location: location.trim() || undefined,
        timeline: timeline.trim() || undefined,
        status: publish ? 'published' : projectStatus,
      };

      await apiRequest(`/projects/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });

      navigate(`/projects/${id}`);
    } catch (err) {
      setServerError(err.message || 'Failed to update project.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleArchive = async () => {
    if (!window.confirm('Are you sure you want to archive this project showcase? It will no longer be visible in discovery.')) {
      return;
    }
    try {
      await apiRequest(`/projects/${id}/archive`, { method: 'POST' });
      navigate('/dashboard/entrepreneur');
    } catch (err) {
      alert(err.message || 'Failed to archive project.');
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 36, height: 36 }} />
      </div>
    );
  }

  return (
    <div className="section" style={{ paddingTop: 36, paddingBottom: 64, minHeight: '85vh' }}>
      <div className="container" style={{ maxWidth: 900 }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>
            <Link to="/dashboard/entrepreneur" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Dashboard</Link>
            <span>/</span>
            <Link to={`/projects/${id}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>{title || 'Project'}</Link>
            <span>/</span>
            <span style={{ color: 'var(--brand-cyan)' }}>Edit Showcase</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                <h1 style={{ fontSize: 28, fontWeight: 800 }}>Edit Project Showcase</h1>
                <Badge variant={projectStatus === 'draft' ? 'amber' : 'cyan'}>
                  {projectStatus}
                </Badge>
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                Update your startup details, milestones, and required resources.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <Button variant="ghost" onClick={handleArchive}>
                Archive
              </Button>
              {projectStatus === 'draft' && (
                <Button variant="emerald" onClick={() => handleUpdate(true)} isLoading={isSubmitting}>
                  Publish Showcase ✓
                </Button>
              )}
              <Button variant="primary" onClick={() => handleUpdate(false)} isLoading={isSubmitting}>
                Save Changes
              </Button>
            </div>
          </div>
        </div>

        {serverError && (
          <div className="alert alert-error" style={{ marginBottom: 24 }}>
            <span>{serverError}</span>
          </div>
        )}

        {/* Section 1: Overview */}
        <div className="card" style={{ marginBottom: 24, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="cyan">Step 1</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Identity & Overview</h3>
          </div>

          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input
              type="text"
              className={`form-input ${errors.title ? 'input-error' : ''}`}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Tagline</label>
            <input
              type="text"
              className={`form-input ${errors.tagline ? 'input-error' : ''}`}
              value={tagline}
              onChange={(e) => setTagline(e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Industry Sub-Sector</label>
              <input
                type="text"
                className="form-input"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Startup Stage</label>
              <select className="form-select" value={stage} onChange={(e) => setStage(e.target.value)}>
                {STAGES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Logo Image URL</label>
              <input
                type="url"
                className="form-input"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Cover / Banner Image URL</label>
              <input
                type="url"
                className="form-input"
                value={coverImageUrl}
                onChange={(e) => setCoverImageUrl(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Location</label>
            <input
              type="text"
              className="form-input"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
        </div>

        {/* Section 2: Problem & Solution */}
        <div className="card" style={{ marginBottom: 24, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="indigo">Step 2</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Problem, Solution & Market</h3>
          </div>

          <div className="form-group">
            <label className="form-label">Problem Statement</label>
            <textarea
              className={`form-textarea ${errors.problemStatement ? 'input-error' : ''}`}
              rows={3}
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Proposed Solution</label>
            <textarea
              className={`form-textarea ${errors.proposedSolution ? 'input-error' : ''}`}
              rows={3}
              value={proposedSolution}
              onChange={(e) => setProposedSolution(e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Target Users / Market</label>
              <textarea
                className={`form-textarea ${errors.targetMarket ? 'input-error' : ''}`}
                rows={2}
                value={targetMarket}
                onChange={(e) => setTargetMarket(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Unique Value Proposition</label>
              <textarea
                className={`form-textarea ${errors.valueProposition ? 'input-error' : ''}`}
                rows={2}
                value={valueProposition}
                onChange={(e) => setValueProposition(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Comprehensive Description</label>
            <textarea
              className={`form-textarea ${errors.description ? 'input-error' : ''}`}
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>

        {/* Section 3: Technical & Progress */}
        <div className="card" style={{ marginBottom: 24, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="purple">Step 3</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Technology, Progress & Assets</h3>
          </div>

          <div className="form-group">
            <label className="form-label">Current Progress</label>
            <textarea
              className="form-textarea"
              rows={2}
              value={currentProgress}
              onChange={(e) => setCurrentProgress(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Technology / Tech Stack</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
              {techStack.map((tech) => (
                <span
                  key={tech}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    color: 'var(--brand-cyan)',
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  {tech}
                  <button
                    type="button"
                    onClick={() => handleRemoveTech(tech)}
                    style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              className="form-input"
              placeholder="Add technology and press Enter..."
              value={techStackInput}
              onChange={(e) => setTechStackInput(e.target.value)}
              onKeyDown={handleAddTech}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Skills Needed</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
              {skillsNeeded.map((skill) => (
                <span
                  key={skill}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    color: 'var(--brand-emerald)',
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              className="form-input"
              placeholder="Add skill and press Enter..."
              value={skillsNeededInput}
              onChange={(e) => setSkillsNeededInput(e.target.value)}
              onKeyDown={handleAddSkill}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Website / Demo URL</label>
              <input
                type="url"
                className="form-input"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Pitch Deck URL</label>
              <input
                type="url"
                className="form-input"
                value={pitchDeckUrl}
                onChange={(e) => setPitchDeckUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Video / Demo URL</label>
              <input
                type="url"
                className="form-input"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Section 4: Funding & Support */}
        <div className="card" style={{ marginBottom: 32, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="emerald">Step 4</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Funding Goals & Required Support</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Funding Goal (₹)</label>
              <input
                type="number"
                className="form-input"
                value={fundingGoal}
                onChange={(e) => setFundingGoal(e.target.value)}
                min={1000}
                step={1000}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Funding Received (₹)</label>
              <input
                type="number"
                className="form-input"
                value={fundingReceived}
                onChange={(e) => setFundingReceived(e.target.value)}
                min={0}
                step={1000}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Required Support Categories</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {SUPPORT_TYPES.map((type) => {
                const isSelected = requiredSupport.includes(type);
                return (
                  <button
                    key={type}
                    type="button"
                    onClick={() => toggleSupportType(type)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                      color: isSelected ? 'var(--brand-emerald)' : 'var(--text-secondary)',
                      border: isSelected ? '1px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
                      transition: 'all 0.15s ease',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <span>{isSelected ? '✓' : '+'}</span>
                    <span>{type}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Specific Resources Detail</label>
              <textarea
                className="form-textarea"
                rows={2}
                value={requiredResources}
                onChange={(e) => setRequiredResources(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Execution Timeline</label>
              <textarea
                className="form-textarea"
                rows={2}
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 20,
            backgroundColor: 'rgba(18, 25, 39, 0.9)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <Button variant="ghost" onClick={() => navigate(`/projects/${id}`)}>
            Cancel
          </Button>

          <div style={{ display: 'flex', gap: 12 }}>
            {projectStatus === 'draft' && (
              <Button variant="emerald" onClick={() => handleUpdate(true)} isLoading={isSubmitting}>
                Publish Showcase
              </Button>
            )}
            <Button variant="primary" onClick={() => handleUpdate(false)} isLoading={isSubmitting}>
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
