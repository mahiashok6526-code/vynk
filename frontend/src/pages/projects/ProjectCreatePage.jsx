import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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

export function ProjectCreatePage() {
  const navigate = useNavigate();

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
  const [requiredSupport, setRequiredSupport] = useState(['Capital']);
  const [requiredResources, setRequiredResources] = useState('');
  const [timeline, setTimeline] = useState('');

  // UI State
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  // Tag Helpers
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
      newErrors.title = 'Project title is required (minimum 2 characters).';
    }

    if (isPublishing) {
      if (!tagline.trim() || tagline.trim().length < 5) {
        newErrors.tagline = 'A concise tagline is required (minimum 5 characters).';
      }
      if (!description.trim() || description.trim().length < 10) {
        newErrors.description = 'Detailed description is required (minimum 10 characters).';
      }
      if (!problemStatement.trim() || problemStatement.trim().length < 10) {
        newErrors.problemStatement = 'Please clearly articulate the problem being solved (minimum 10 characters).';
      }
      if (!proposedSolution.trim() || proposedSolution.trim().length < 10) {
        newErrors.proposedSolution = 'Please explain your proposed innovative solution (minimum 10 characters).';
      }
      if (!targetMarket.trim() || targetMarket.trim().length < 5) {
        newErrors.targetMarket = 'Please specify your target users or customer segment.';
      }
      if (!valueProposition.trim() || valueProposition.trim().length < 5) {
        newErrors.valueProposition = 'Please explain your unique value proposition.';
      }
      if (!fundingGoal || Number(fundingGoal) <= 0) {
        newErrors.fundingGoal = 'Funding goal must be a positive number greater than 0.';
      }
      if (!requiredSupport || requiredSupport.length === 0) {
        newErrors.requiredSupport = 'Select at least one type of support required.';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (publish) => {
    setServerError('');
    const isValid = validateForm(publish);
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
        status: publish ? 'published' : 'draft',
      };

      const res = await apiRequest('/projects/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      if (publish) {
        navigate(`/projects/${res.id}`);
      } else {
        navigate('/dashboard/entrepreneur');
      }
    } catch (err) {
      setServerError(err.message || 'Failed to create project showcase.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="section" style={{ paddingTop: 36, paddingBottom: 64, minHeight: '85vh' }}>
      <div className="container" style={{ maxWidth: 900 }}>
        {/* Breadcrumb & Header */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>
            <Link to="/dashboard/entrepreneur" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Dashboard</Link>
            <span>/</span>
            <span style={{ color: 'var(--brand-cyan)' }}>New Project Showcase</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 6 }}>Create Project Showcase</h1>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                Publish your venture to connect with verified sponsors, investors, and strategic mentors.
              </p>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Button
                variant="ghost"
                onClick={() => handleSubmit(false)}
                disabled={isSubmitting}
              >
                Save as Draft
              </Button>
              <Button
                variant="primary"
                onClick={() => handleSubmit(true)}
                isLoading={isSubmitting}
              >
                Publish Project Showcase →
              </Button>
            </div>
          </div>
        </div>

        {serverError && (
          <div className="alert alert-error" style={{ marginBottom: 24 }}>
            <span>{serverError}</span>
          </div>
        )}

        {Object.keys(errors).length > 0 && (
          <div className="alert alert-error" style={{ marginBottom: 24 }}>
            <strong>Please fix the following validation errors before publishing:</strong>
            <ul style={{ marginTop: 8, paddingLeft: 20 }}>
              {Object.values(errors).map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Section 1: Identity & Basics */}
        <div className="card" style={{ marginBottom: 24, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="cyan">Step 1</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Identity & Overview</h3>
          </div>

          <div className="form-group">
            <label className="form-label">
              Project / Startup Name <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <input
              type="text"
              className={`form-input ${errors.title ? 'input-error' : ''}`}
              placeholder="e.g. AlgaFlux BioSequestration"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            {errors.title && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.title}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">
              One-Line Tagline <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <input
              type="text"
              className={`form-input ${errors.tagline ? 'input-error' : ''}`}
              placeholder="e.g. Modular algal bioreactors abating point-source industrial CO2"
              value={tagline}
              onChange={(e) => setTagline(e.target.value)}
              maxLength={300}
            />
            {errors.tagline && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.tagline}</span>}
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
                placeholder="e.g. Carbon Capture & Clean Energy"
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
                placeholder="https://... (PNG/SVG logo)"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Cover / Banner Image URL</label>
              <input
                type="url"
                className="form-input"
                placeholder="https://... (Unsplash or hosted banner)"
                value={coverImageUrl}
                onChange={(e) => setCoverImageUrl(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Headquarters / Location</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Austin, TX, USA or Remote"
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
            <label className="form-label">
              Problem Being Solved <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <textarea
              className={`form-textarea ${errors.problemStatement ? 'input-error' : ''}`}
              rows={3}
              placeholder="What core bottleneck, friction, or inefficiency exists today? Why is existing technology inadequate?"
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
            />
            {errors.problemStatement && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.problemStatement}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">
              Proposed Solution <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <textarea
              className={`form-textarea ${errors.proposedSolution ? 'input-error' : ''}`}
              rows={3}
              placeholder="How does your technology or product solve this problem? What is your proprietary approach?"
              value={proposedSolution}
              onChange={(e) => setProposedSolution(e.target.value)}
            />
            {errors.proposedSolution && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.proposedSolution}</span>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">
                Target Users / Customers <span style={{ color: 'var(--brand-cyan)' }}>*</span>
              </label>
              <textarea
                className={`form-textarea ${errors.targetMarket ? 'input-error' : ''}`}
                rows={2}
                placeholder="e.g. Enterprise manufacturing plants, Tier-1 suppliers..."
                value={targetMarket}
                onChange={(e) => setTargetMarket(e.target.value)}
              />
              {errors.targetMarket && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.targetMarket}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">
                Unique Value Proposition <span style={{ color: 'var(--brand-cyan)' }}>*</span>
              </label>
              <textarea
                className={`form-textarea ${errors.valueProposition ? 'input-error' : ''}`}
                rows={2}
                placeholder="Why do you win? e.g. 10x lower capital expenditure with zero retrofitting..."
                value={valueProposition}
                onChange={(e) => setValueProposition(e.target.value)}
              />
              {errors.valueProposition && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.valueProposition}</span>}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              Comprehensive Description <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <textarea
              className={`form-textarea ${errors.description ? 'input-error' : ''}`}
              rows={4}
              placeholder="Detailed background of the initiative, founding journey, traction to date, and roadmap..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            {errors.description && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.description}</span>}
          </div>
        </div>

        {/* Section 3: Technical & Progress */}
        <div className="card" style={{ marginBottom: 24, border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Badge variant="purple">Step 3</Badge>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Technology, Progress & Assets</h3>
          </div>

          <div className="form-group">
            <label className="form-label">Current Progress & Milestones Achieved</label>
            <textarea
              className="form-textarea"
              rows={2}
              placeholder="e.g. Completed laboratory bench proof of concept, signed letters of intent with 2 industrial pilots..."
              value={currentProgress}
              onChange={(e) => setCurrentProgress(e.target.value)}
            />
          </div>

          {/* Tech Stack Chips */}
          <div className="form-group">
            <label className="form-label">Technology / Tech Stack (Press Enter to add)</label>
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
                    style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: 14 }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              className="form-input"
              placeholder="Type technology (e.g. Rust, PyTorch, Embedded C++) and press Enter..."
              value={techStackInput}
              onChange={(e) => setTechStackInput(e.target.value)}
              onKeyDown={handleAddTech}
            />
          </div>

          {/* Skills Needed Chips */}
          <div className="form-group">
            <label className="form-label">Key Skills Needed (Press Enter to add)</label>
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
                    style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: 14 }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              className="form-input"
              placeholder="Type skill needed (e.g. Hardware Engineering, Regulatory Compliance) and press Enter..."
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
                placeholder="https://..."
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Pitch Deck URL</label>
              <input
                type="url"
                className="form-input"
                placeholder="https://... (Docsend or PDF link)"
                value={pitchDeckUrl}
                onChange={(e) => setPitchDeckUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Video / Demo URL</label>
              <input
                type="url"
                className="form-input"
                placeholder="https://... (YouTube, Vimeo or Loom)"
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
              <label className="form-label">
                Funding Goal (₹) <span style={{ color: 'var(--brand-cyan)' }}>*</span>
              </label>
              <input
                type="number"
                className={`form-input ${errors.fundingGoal ? 'input-error' : ''}`}
                value={fundingGoal}
                onChange={(e) => setFundingGoal(e.target.value)}
                min={1000}
                step={1000}
              />
              {errors.fundingGoal && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12 }}>{errors.fundingGoal}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Funding Already Received (₹)</label>
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

          {/* Required Support Checkboxes */}
          <div className="form-group">
            <label className="form-label">
              Required Support Categories <span style={{ color: 'var(--brand-cyan)' }}>*</span>
            </label>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 10 }}>
              Select all resource types you are seeking from sponsors:
            </p>
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
            {errors.requiredSupport && <span className="field-error-text" style={{ color: '#EF4444', fontSize: 12, marginTop: 6, display: 'block' }}>{errors.requiredSupport}</span>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Specific Resources Detail</label>
              <textarea
                className="form-textarea"
                rows={2}
                placeholder="e.g. 5,000 GPU compute hours, access to wet lab biosafety level 2..."
                value={requiredResources}
                onChange={(e) => setRequiredResources(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Expected Execution Timeline</label>
              <textarea
                className="form-textarea"
                rows={2}
                placeholder="e.g. Q4 2026: Prototype validation. Q2 2027: Commercial deployment..."
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Bottom Submission Actions */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 16,
            padding: 20,
            backgroundColor: 'rgba(18, 25, 39, 0.9)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div>
            <div style={{ fontSize: 14, fontWeight: 600 }}>Ready to share your innovation?</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Published showcases immediately appear in the verified sponsor discovery feed.
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <Button
              variant="ghost"
              onClick={() => handleSubmit(false)}
              disabled={isSubmitting}
            >
              Save as Draft
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => handleSubmit(true)}
              isLoading={isSubmitting}
            >
              Publish Project Showcase →
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
