import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { ProjectCard } from '../../components/project/ProjectCard';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { formatCurrency } from '../../utils/currency';

const CATEGORIES = [
  'All Categories',
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

const INDUSTRIES = [
  'All Industries',
  'Climate & Energy',
  'Healthcare & Bio',
  'Autonomous Systems',
  'Financial Services',
  'Industrial Manufacturing',
  'Enterprise Software',
  'Agriculture',
];

const STAGES = [
  { label: 'All Stages', value: '' },
  { label: 'Idea', value: 'idea' },
  { label: 'Prototype', value: 'prototype' },
  { label: 'MVP', value: 'mvp' },
  { label: 'Launched', value: 'launched' },
  { label: 'Scaling', value: 'scaling' },
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

export function ProjectsDiscoveryPage() {
  const { user, isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;
  const [isLoading, setIsLoading] = useState(true);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedIndustry, setSelectedIndustry] = useState('All Industries');
  const [selectedStage, setSelectedStage] = useState('');
  const [selectedSupport, setSelectedSupport] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [minFunding, setMinFunding] = useState('');
  const [maxFunding, setMaxFunding] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  // Proposal modal state for Sponsors
  const [sponsorTarget, setSponsorTarget] = useState(null);
  const [commitmentAmount, setCommitmentAmount] = useState(250000);
  const [sponsorshipType, setSponsorshipType] = useState('grant');
  const [commitmentNotes, setCommitmentNotes] = useState('');
  const [isSubmittingProposal, setIsSubmittingProposal] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ type: '', text: '' });

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.append('search', searchTerm.trim());
      if (selectedCategory && selectedCategory !== 'All Categories') params.append('category', selectedCategory);
      if (selectedIndustry && selectedIndustry !== 'All Industries') params.append('industry', selectedIndustry);
      if (selectedStage) params.append('stage', selectedStage);
      if (selectedSupport) params.append('required_support', selectedSupport);
      if (selectedStatus) params.append('status', selectedStatus);
      if (locationInput.trim()) params.append('location', locationInput.trim());
      if (minFunding) params.append('min_funding', minFunding);
      if (maxFunding) params.append('max_funding', maxFunding);
      if (sortBy) params.append('sort', sortBy);

      params.append('page', currentPage);
      params.append('limit', pageSize);

      const queryString = `?${params.toString()}`;
      const data = await apiRequest(`/projects/${queryString}`);

      if (data && data.results !== undefined) {
        setProjects(data.results || []);
        setTotalCount(data.total || 0);
        setTotalPages(data.total_pages || 1);
      } else if (Array.isArray(data)) {
        setProjects(data);
        setTotalCount(data.length);
        setTotalPages(1);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setIsLoading(false);
    }
  }, [
    searchTerm,
    selectedCategory,
    selectedIndustry,
    selectedStage,
    selectedSupport,
    selectedStatus,
    locationInput,
    minFunding,
    maxFunding,
    sortBy,
    currentPage,
  ]);

  // Trigger query on filter change (resets to page 1)
  useEffect(() => {
    setCurrentPage(1);
  }, [
    searchTerm,
    selectedCategory,
    selectedIndustry,
    selectedStage,
    selectedSupport,
    selectedStatus,
    locationInput,
    minFunding,
    maxFunding,
    sortBy,
  ]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProjects();
    }, 250);
    return () => clearTimeout(timer);
  }, [fetchProjects]);

  const handleClearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('All Categories');
    setSelectedIndustry('All Industries');
    setSelectedStage('');
    setSelectedSupport('');
    setSelectedStatus('');
    setLocationInput('');
    setMinFunding('');
    setMaxFunding('');
    setSortBy('recent');
    setCurrentPage(1);
  };

  const handleProposeSponsorship = async (e) => {
    e.preventDefault();
    if (!sponsorTarget) return;

    setIsSubmittingProposal(true);
    setStatusMessage({ type: '', text: '' });

    try {
      await apiRequest('/commitments/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: sponsorTarget.id,
          amount: Number(commitmentAmount),
          sponsorship_type: sponsorshipType,
          status: 'interested',
          notes: commitmentNotes.trim() || undefined,
        }),
      });
      setStatusMessage({
        type: 'success',
        text: `Sponsorship interest of ${formatCurrency(commitmentAmount, sponsorTarget.currency || 'INR')} proposed to ${sponsorTarget.title}!`,
      });
      setSponsorTarget(null);
      setCommitmentNotes('');
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message || 'Failed to submit commitment proposal.',
      });
    } finally {
      setIsSubmittingProposal(false);
    }
  };

  // Active filter chip descriptors
  const activeChips = [];
  if (searchTerm.trim()) {
    activeChips.push({ label: `Search: "${searchTerm}"`, onRemove: () => setSearchTerm('') });
  }
  if (selectedCategory !== 'All Categories') {
    activeChips.push({ label: `Category: ${selectedCategory}`, onRemove: () => setSelectedCategory('All Categories') });
  }
  if (selectedIndustry !== 'All Industries') {
    activeChips.push({ label: `Industry: ${selectedIndustry}`, onRemove: () => setSelectedIndustry('All Industries') });
  }
  if (selectedStage) {
    const sObj = STAGES.find((s) => s.value === selectedStage);
    activeChips.push({ label: `Stage: ${sObj ? sObj.label : selectedStage}`, onRemove: () => setSelectedStage('') });
  }
  if (selectedSupport) {
    activeChips.push({ label: `Support: ${selectedSupport}`, onRemove: () => setSelectedSupport('') });
  }
  if (selectedStatus) {
    activeChips.push({ label: `Status: ${selectedStatus.replace('_', ' ')}`, onRemove: () => setSelectedStatus('') });
  }
  if (locationInput.trim()) {
    activeChips.push({ label: `Location: ${locationInput}`, onRemove: () => setLocationInput('') });
  }
  if (minFunding) {
    activeChips.push({ label: `Min Goal: ${formatCurrency(minFunding, 'INR')}`, onRemove: () => setMinFunding('') });
  }
  if (maxFunding) {
    activeChips.push({ label: `Max Goal: ${formatCurrency(maxFunding, 'INR')}`, onRemove: () => setMaxFunding('') });
  }

  return (
    <div className="section" style={{ paddingTop: 36, minHeight: '85vh' }}>
      <div className="container">
        {/* Top Hero Banner */}
        <div
          className="card"
          style={{
            marginBottom: 28,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(6, 182, 212, 0.08) 100%)',
            border: '1px solid var(--border-subtle)',
            padding: '36px 32px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 20 }}>
            <div style={{ maxWidth: 720 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <Badge variant="cyan">Explore Projects & Ventures</Badge>
                <Badge variant="emerald">Primary Currency: INR (₹)</Badge>
              </div>
              <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 10, letterSpacing: '-0.02em' }}>
                Discover High-Impact Innovations & Startups
              </h1>
              <p style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Explore vetted startup showcases seeking capital, compute credits, and strategic mentorship. Back verified founders with transparent milestone tracking.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <Link to="/sponsors" style={{ textDecoration: 'none' }}>
                <Button variant="secondary" size="md">
                  Explore Sponsors →
                </Button>
              </Link>
              {isAuthenticated && user?.role === 'entrepreneur' && (
                <Link to="/projects/new" style={{ textDecoration: 'none' }}>
                  <Button variant="primary" size="md">
                    + Create Project Showcase
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>

        {statusMessage.text && (
          <div className={`alert alert-${statusMessage.type}`} style={{ marginBottom: 24 }}>
            <span>{statusMessage.text}</span>
          </div>
        )}

        {/* Filter Controls Bar */}
        <div
          className="card"
          style={{
            marginBottom: 24,
            padding: 24,
            border: '1px solid var(--border-subtle)',
            backgroundColor: 'rgba(13, 18, 29, 0.7)',
          }}
        >
          {/* Row 1: Search, Category, Industry, Status */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 16 }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Search Showcases</label>
              <input
                type="text"
                className="form-input"
                placeholder="Search name, problem, tech..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Category</label>
              <select
                className="form-select"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Industry</label>
              <select
                className="form-select"
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
              >
                {INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Status</label>
              <select
                className="form-select"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                <option value="">All Discoverable Statuses</option>
                <option value="seeking_sponsorship">Seeking Sponsorship</option>
                <option value="published">Published</option>
                <option value="in_discussion">In Discussion</option>
                <option value="funded">Funded</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          {/* Row 2: Location & Funding Range Inputs (in ₹) & Sort */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 16 }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Location</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Bengaluru, Mumbai, Remote"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Min Funding Goal (₹)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 50000"
                value={minFunding}
                onChange={(e) => setMinFunding(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Max Funding Goal (₹)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 5000000"
                value={maxFunding}
                onChange={(e) => setMaxFunding(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Sort Order</label>
              <select
                className="form-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="recent">Most Recent</option>
                <option value="updated">Recently Updated</option>
                <option value="funding_high">Highest Funding Goal (₹)</option>
                <option value="funding_low">Lowest Funding Goal (₹)</option>
                <option value="progress">Funding Progress</option>
                <option value="title">Project Name (A-Z)</option>
              </select>
            </div>
          </div>

          {/* Row 3: Stage Filter Pills */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 14 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>Stage:</span>
            {STAGES.map((s) => {
              const active = selectedStage === s.value;
              return (
                <button
                  key={s.label}
                  onClick={() => setSelectedStage(active ? '' : s.value)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 12,
                    fontWeight: active ? 600 : 400,
                    cursor: 'pointer',
                    backgroundColor: active ? 'var(--brand-cyan)' : 'rgba(255, 255, 255, 0.05)',
                    color: active ? '#07090E' : 'var(--text-secondary)',
                    border: active ? '1px solid var(--brand-cyan)' : '1px solid var(--border-subtle)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {s.label}
                </button>
              );
            })}
          </div>

          {/* Row 4: Required Support Types */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>Required Support:</span>
            {SUPPORT_TYPES.map((supp) => {
              const active = selectedSupport === supp;
              return (
                <button
                  key={supp}
                  onClick={() => setSelectedSupport(active ? '' : supp)}
                  style={{
                    padding: '3px 10px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 11,
                    fontWeight: active ? 600 : 400,
                    cursor: 'pointer',
                    backgroundColor: active ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    color: active ? 'var(--brand-emerald)' : 'var(--text-secondary)',
                    border: active ? '1px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {supp}
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Filter Chips */}
        {activeChips.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 8,
              marginBottom: 20,
              padding: '12px 16px',
              backgroundColor: 'rgba(6, 182, 212, 0.06)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(6, 182, 212, 0.15)',
            }}
          >
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--brand-cyan)' }}>
              Active Filters:
            </span>
            {activeChips.map((chip, i) => (
              <span
                key={i}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: 12,
                  color: 'var(--text-primary)',
                }}
              >
                <span>{chip.label}</span>
                <button
                  onClick={chip.onRemove}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--brand-cyan)',
                    cursor: 'pointer',
                    fontSize: 13,
                    padding: 0,
                  }}
                >
                  ✕
                </button>
              </span>
            ))}
            <button
              onClick={handleClearFilters}
              style={{
                marginLeft: 'auto',
                background: 'none',
                border: 'none',
                color: 'var(--brand-cyan)',
                fontSize: 12,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Reset All Filters
            </button>
          </div>
        )}

        {/* Results Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>
            {isLoading ? 'Searching...' : `Available Showcases (${totalCount})`}
          </h2>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Showing page {currentPage} of {totalPages}
          </span>
        </div>

        {/* Projects Grid */}
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '30vh' }}>
            <div className="spinner" style={{ width: 36, height: 36 }} />
          </div>
        ) : projects.length === 0 ? (
          <div
            className="card"
            style={{
              padding: '60px 24px',
              textAlign: 'center',
              backgroundColor: 'rgba(13, 18, 29, 0.5)',
              border: '1px dashed var(--border-subtle)',
            }}
          >
            <div style={{ fontSize: 36, marginBottom: 12 }}>🔍</div>
            <h3 style={{ fontSize: 20, marginBottom: 8 }}>No Showcases Found</h3>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto 20px' }}>
              We couldn't find any published startup showcases matching your active criteria. Try adjusting your search or clearing filters.
            </p>
            <Button variant="secondary" onClick={handleClearFilters}>
              Reset All Filters
            </Button>
          </div>
        ) : (
          <>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: 24,
                marginBottom: 32,
              }}
            >
              {projects.map((proj) => (
                <ProjectCard
                  key={proj.id}
                  project={proj}
                  onSponsor={user?.role === 'sponsor' ? (p) => setSponsorTarget(p) : null}
                />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: 10,
                  marginTop: 24,
                  marginBottom: 32,
                }}
              >
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                >
                  ← Previous
                </Button>

                {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((pg) => (
                  <button
                    key={pg}
                    onClick={() => setCurrentPage(pg)}
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 'var(--radius-sm)',
                      border: pg === currentPage ? '1px solid var(--brand-cyan)' : '1px solid var(--border-subtle)',
                      backgroundColor: pg === currentPage ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                      color: pg === currentPage ? 'var(--brand-cyan)' : 'var(--text-secondary)',
                      fontWeight: pg === currentPage ? 700 : 400,
                      cursor: 'pointer',
                      fontSize: 13,
                    }}
                  >
                    {pg}
                  </button>
                ))}

                <Button
                  variant="ghost"
                  size="sm"
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                >
                  Next →
                </Button>
              </div>
            )}
          </>
        )}

        {/* Propose Sponsorship Modal (for Sponsors) */}
        {sponsorTarget && (
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
            <div className="card" style={{ maxWidth: 540, width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontSize: 20, fontWeight: 700 }}>Propose Sponsorship Commitment</h3>
                <button
                  onClick={() => setSponsorTarget(null)}
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
                <div style={{ fontSize: 11, color: 'var(--brand-cyan)', fontWeight: 700, textTransform: 'uppercase' }}>Target Initiative</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>{sponsorTarget.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Founder: {sponsorTarget.founder?.full_name || 'Vynk Entrepreneur'}</div>
              </div>

              <form onSubmit={handleProposeSponsorship}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Sponsorship Allocation (₹)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={commitmentAmount}
                      onChange={(e) => setCommitmentAmount(e.target.value)}
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
                  <label className="form-label">Proposed Collaboration & Terms</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    placeholder="Specify tranche expectations, technical alignment, or discussion schedule..."
                    value={commitmentNotes}
                    onChange={(e) => setCommitmentNotes(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                  <Button variant="ghost" onClick={() => setSponsorTarget(null)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="emerald" isLoading={isSubmittingProposal}>
                    Submit Sponsorship Proposal
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
