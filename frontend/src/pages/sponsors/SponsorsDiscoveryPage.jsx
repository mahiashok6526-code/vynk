import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { SponsorCard } from '../../components/sponsor/SponsorCard';
import { ConnectModal } from '../../components/sponsor/ConnectModal';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { formatCurrency } from '../../utils/currency';

const SPONSOR_TYPES = [
  { label: 'All Sponsor Types', value: '' },
  { label: 'Individual Angel Investor', value: 'individual_angel' },
  { label: 'Venture Capital Fund', value: 'venture_capital' },
  { label: 'Corporate Accelerator', value: 'corporate_accelerator' },
  { label: 'Grant Foundation', value: 'grant_foundation' },
  { label: 'Angel Syndicate', value: 'angel_network' },
];

const INDUSTRIES = [
  'All Sectors',
  'DeepTech',
  'CleanTech',
  'AI & Robotics',
  'HealthTech',
  'FinTech',
  'AgTech',
  'Enterprise Software',
];

const SUPPORT_AREAS = [
  'Capital',
  'Compute Credits',
  'Mentorship',
  'Labs & Facilities',
  'Regulatory Support',
  'Enterprise Pilot Access',
];

export function SponsorsDiscoveryPage() {
  const { user, isAuthenticated } = useAuth();
  const [sponsors, setSponsors] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;
  const [isLoading, setIsLoading] = useState(true);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('All Sectors');
  const [selectedArea, setSelectedArea] = useState('');
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [isVerifiedOnly, setIsVerifiedOnly] = useState(false);
  const [sortBy, setSortBy] = useState('recent');

  // Connect Modal State
  const [activeSponsorForConnect, setActiveSponsorForConnect] = useState(null);
  const [toastMessage, setToastMessage] = useState('');

  const fetchSponsors = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.append('search', searchTerm.trim());
      if (selectedType) params.append('sponsor_type', selectedType);
      if (selectedIndustry && selectedIndustry !== 'All Sectors') params.append('industry', selectedIndustry);
      if (selectedArea) params.append('sponsorship_type', selectedArea);
      if (minBudget) params.append('min_budget', minBudget);
      if (maxBudget) params.append('max_budget', maxBudget);
      if (locationInput.trim()) params.append('location', locationInput.trim());
      if (isVerifiedOnly) params.append('is_verified', 'true');
      if (sortBy) params.append('sort', sortBy);

      params.append('page', currentPage);
      params.append('limit', pageSize);

      const queryString = `?${params.toString()}`;
      const data = await apiRequest(`/sponsors/${queryString}`);

      if (data && data.results !== undefined) {
        setSponsors(data.results || []);
        setTotalCount(data.total || 0);
        setTotalPages(data.total_pages || 1);
      } else if (Array.isArray(data)) {
        setSponsors(data);
        setTotalCount(data.length);
        setTotalPages(1);
      }
    } catch (err) {
      console.error('Failed to load sponsors:', err);
    } finally {
      setIsLoading(false);
    }
  }, [
    searchTerm,
    selectedType,
    selectedIndustry,
    selectedArea,
    minBudget,
    maxBudget,
    locationInput,
    isVerifiedOnly,
    sortBy,
    currentPage,
  ]);

  // Reset to page 1 on filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [
    searchTerm,
    selectedType,
    selectedIndustry,
    selectedArea,
    minBudget,
    maxBudget,
    locationInput,
    isVerifiedOnly,
    sortBy,
  ]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSponsors();
    }, 250);
    return () => clearTimeout(timer);
  }, [fetchSponsors]);

  const handleClearFilters = () => {
    setSearchTerm('');
    setSelectedType('');
    setSelectedIndustry('All Sectors');
    setSelectedArea('');
    setMinBudget('');
    setMaxBudget('');
    setLocationInput('');
    setIsVerifiedOnly(false);
    setSortBy('recent');
    setCurrentPage(1);
  };

  // Active filter chip descriptors
  const activeChips = [];
  if (searchTerm.trim()) {
    activeChips.push({ label: `Search: "${searchTerm}"`, onRemove: () => setSearchTerm('') });
  }
  if (selectedType) {
    const tObj = SPONSOR_TYPES.find((t) => t.value === selectedType);
    activeChips.push({ label: `Type: ${tObj ? tObj.label : selectedType}`, onRemove: () => setSelectedType('') });
  }
  if (selectedIndustry !== 'All Sectors') {
    activeChips.push({ label: `Sector: ${selectedIndustry}`, onRemove: () => setSelectedIndustry('All Sectors') });
  }
  if (selectedArea) {
    activeChips.push({ label: `Support: ${selectedArea}`, onRemove: () => setSelectedArea('') });
  }
  if (minBudget) {
    activeChips.push({ label: `Min Budget: ${formatCurrency(minBudget, 'INR')}`, onRemove: () => setMinBudget('') });
  }
  if (maxBudget) {
    activeChips.push({ label: `Max Budget: ${formatCurrency(maxBudget, 'INR')}`, onRemove: () => setMaxBudget('') });
  }
  if (locationInput.trim()) {
    activeChips.push({ label: `Location: ${locationInput}`, onRemove: () => setLocationInput('') });
  }
  if (isVerifiedOnly) {
    activeChips.push({ label: 'Verified Partners Only', onRemove: () => setIsVerifiedOnly(false) });
  }

  return (
    <div className="section" style={{ paddingTop: 36, minHeight: '85vh' }}>
      <div className="container">
        {/* Top Hero Banner */}
        <div
          className="card"
          style={{
            marginBottom: 28,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(16, 185, 129, 0.08) 100%)',
            border: '1px solid var(--border-subtle)',
            padding: '36px 32px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 20 }}>
            <div style={{ maxWidth: 720 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <Badge variant="emerald">Sponsor & Capital Discovery</Badge>
                <Badge variant="cyan">Primary Currency: INR (₹)</Badge>
              </div>
              <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 10, letterSpacing: '-0.02em' }}>
                Discover Verified Sponsors & Funding Partners
              </h1>
              <p style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Explore active angel investors, venture funds, and corporate labs deployable across high-growth startups. Connect with transparent capital and verifiable trust.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <Link to="/projects" style={{ textDecoration: 'none' }}>
                <Button variant="secondary" size="md">
                  Explore Project Showcases →
                </Button>
              </Link>
              {isAuthenticated && user?.role === 'entrepreneur' && (
                <Link to="/projects/new" style={{ textDecoration: 'none' }}>
                  <Button variant="primary" size="md">
                    + Publish Showcase
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>

        {toastMessage && (
          <div className="alert alert-success" style={{ marginBottom: 24 }}>
            <span>{toastMessage}</span>
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
          {/* Row 1: Search, Sponsor Type, Industry */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 16 }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Search Partners</label>
              <input
                type="text"
                className="form-input"
                placeholder="Search name, organization, sector..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Sponsor Type</label>
              <select
                className="form-select"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                {SPONSOR_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Sector Focus</label>
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
          </div>

          {/* Row 2: Location, Budget Range (in ₹), Sort */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 16 }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Location</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Bengaluru, Delhi, Remote"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Min Budget (₹)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 50000"
                value={minBudget}
                onChange={(e) => setMinBudget(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: 12 }}>Max Budget (₹)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 5000000"
                value={maxBudget}
                onChange={(e) => setMaxBudget(e.target.value)}
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
                <option value="budget_high">Highest Budget (₹)</option>
                <option value="budget_low">Lowest Budget (₹)</option>
                <option value="trust">Highest Trust Score</option>
                <option value="name">Partner Name (A-Z)</option>
              </select>
            </div>
          </div>

          {/* Row 3: Supported Areas Pills & Verified Checkbox */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>Supported Areas:</span>
              {SUPPORT_AREAS.map((area) => {
                const active = selectedArea === area;
                return (
                  <button
                    key={area}
                    onClick={() => setSelectedArea(active ? '' : area)}
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
                    {area}
                  </button>
                );
              })}
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13, color: 'var(--text-secondary)' }}>
              <input
                type="checkbox"
                checked={isVerifiedOnly}
                onChange={(e) => setIsVerifiedOnly(e.target.checked)}
                style={{ cursor: 'pointer', accentColor: 'var(--brand-emerald)' }}
              />
              <span>Verified Partners Only</span>
            </label>
          </div>
        </div>

        {/* Active Filter Chips Bar */}
        {activeChips.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 8,
              marginBottom: 20,
              padding: '12px 16px',
              backgroundColor: 'rgba(16, 185, 129, 0.06)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(16, 185, 129, 0.15)',
            }}
          >
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--brand-emerald)' }}>
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
                    color: 'var(--brand-emerald)',
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
                color: 'var(--brand-emerald)',
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
            {isLoading ? 'Searching...' : `Available Capital Partners (${totalCount})`}
          </h2>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Showing page {currentPage} of {totalPages}
          </span>
        </div>

        {/* Sponsors Grid */}
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '30vh' }}>
            <div className="spinner" style={{ width: 36, height: 36 }} />
          </div>
        ) : sponsors.length === 0 ? (
          <div
            className="card"
            style={{
              padding: '60px 24px',
              textAlign: 'center',
              backgroundColor: 'rgba(13, 18, 29, 0.5)',
              border: '1px dashed var(--border-subtle)',
            }}
          >
            <div style={{ fontSize: 36, marginBottom: 12 }}>💼</div>
            <h3 style={{ fontSize: 20, marginBottom: 8 }}>No Capital Partners Found</h3>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto 20px' }}>
              We couldn't find any sponsors matching your active filter criteria. Try broadening your budget range or resetting filters.
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
              {sponsors.map((sp) => (
                <SponsorCard
                  key={sp.id}
                  sponsor={sp}
                  onConnect={(target) => setActiveSponsorForConnect(target)}
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
                      border: pg === currentPage ? '1px solid var(--brand-emerald)' : '1px solid var(--border-subtle)',
                      backgroundColor: pg === currentPage ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                      color: pg === currentPage ? 'var(--brand-emerald)' : 'var(--text-secondary)',
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

        {/* Connect Modal */}
        {activeSponsorForConnect && (
          <ConnectModal
            sponsor={activeSponsorForConnect}
            onClose={() => setActiveSponsorForConnect(null)}
            onSuccess={(msg) => setToastMessage(msg)}
          />
        )}
      </div>
    </div>
  );
}
