import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { TrustScoreBadge } from '../common/TrustScoreBadge';
import { formatCurrency } from '../../utils/currency';

const SUPPORT_TYPES = [
  { value: 'Financial Funding', label: 'Financial Funding (Capital / Grant / Equity)', isMonetary: true },
  { value: 'Hardware', label: 'Hardware / Prototype Equipment', isMonetary: false },
  { value: 'Software / Cloud Credits', label: 'Software / Cloud Credits', isMonetary: false },
  { value: 'Mentorship', label: 'Strategic Mentorship & Advisory', isMonetary: false },
  { value: 'Partnership', label: 'Commercial & Distribution Partnership', isMonetary: false },
  { value: 'Marketing', label: 'Marketing & PR Exposure', isMonetary: false },
  { value: 'Workspace', label: 'Incubator / Workspace Facilities', isMonetary: false },
  { value: 'Testing / Facilities', label: 'Testing & Lab Facilities', isMonetary: false },
  { value: 'Other', label: 'Other Support Vehicle', isMonetary: false },
];

export function ConnectModal({ sponsor, onClose, onSuccess }) {
  const { user, isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [sponsorshipType, setSponsorshipType] = useState('Financial Funding');
  const [proposedAmount, setProposedAmount] = useState(
    sponsor?.min_budget ? Math.min(sponsor.min_budget * 2, sponsor.max_budget) : 250000
  );
  const [requestedResources, setRequestedResources] = useState('');
  const [pitchMessage, setPitchMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const isEntrepreneur = user?.role === 'entrepreneur';
  const selectedTypeObj = SUPPORT_TYPES.find((t) => t.value === sponsorshipType) || SUPPORT_TYPES[0];
  const isMonetary = selectedTypeObj.isMonetary;

  useEffect(() => {
    if (isAuthenticated && isEntrepreneur) {
      apiRequest('/projects/my-projects')
        .then((res) => {
          setProjects(res || []);
          if (res && res.length > 0) {
            setSelectedProjectId(res[0].id);
          }
        })
        .catch(() => setProjects([]));
    }
  }, [isAuthenticated, isEntrepreneur]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      setErrorMsg('Please log in or register to initiate a sponsor connection.');
      return;
    }

    if (!isEntrepreneur) {
      setErrorMsg('Only entrepreneur accounts can propose project sponsorship to funding partners.');
      return;
    }

    if (!selectedProjectId) {
      setErrorMsg('Please select one of your startup showcases to connect.');
      return;
    }

    const recipientUserId = sponsor.user_id || sponsor.id;
    if (!recipientUserId) {
      setErrorMsg('Invalid sponsor target recipient.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      await apiRequest('/sponsorship-requests/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: Number(selectedProjectId),
          recipient_id: Number(recipientUserId),
          sponsorship_type: sponsorshipType,
          requested_amount: isMonetary ? Number(proposedAmount) : undefined,
          requested_resources: requestedResources.trim() || undefined,
          currency: 'INR',
          message: pitchMessage.trim() || 'Interested in exploring sponsorship synergy with your fund.',
        }),
      });

      if (onSuccess) {
        onSuccess(
          `Sponsorship request for ${sponsorshipType} sent to ${
            sponsor.organization_name || sponsor.full_name
          }!`
        );
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to send sponsorship request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
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
      <div className="card" style={{ maxWidth: 560, width: '100%', border: '1px solid var(--border-glow)' }}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <Badge variant="emerald">Sponsorship Request</Badge>
              {sponsor.is_verified && <Badge variant="cyan">Verified Partner</Badge>}
            </div>
            <h3 style={{ fontSize: 20, fontWeight: 700 }}>
              Request Sponsorship from {sponsor.organization_name || sponsor.full_name}
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
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

        {/* Sponsor Overview Snippet */}
        <div
          style={{
            padding: 14,
            backgroundColor: 'rgba(16, 185, 129, 0.08)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            marginBottom: 20,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <div>
            <div style={{ fontSize: 11, color: 'var(--brand-emerald)', fontWeight: 700, textTransform: 'uppercase' }}>
              Target Sponsor
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              {sponsor.full_name} {sponsor.organization_name && `· ${sponsor.organization_name}`}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
              Typical Allocation: {formatCurrency(sponsor.min_budget || 50000, 'INR')} –{' '}
              {formatCurrency(sponsor.max_budget || 1000000, 'INR')}
            </div>
          </div>
          <TrustScoreBadge score={sponsor.trust_score || 50} size="sm" />
        </div>

        {errorMsg && (
          <div className="alert alert-error" style={{ marginBottom: 16 }}>
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isEntrepreneur ? (
            <>
              {/* Pick Project */}
              <div className="form-group">
                <label className="form-label">Select Your Venture Showcase *</label>
                {projects.length === 0 ? (
                  <div
                    style={{
                      padding: 12,
                      backgroundColor: 'rgba(239, 68, 68, 0.08)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid rgba(239, 68, 68, 0.2)',
                      fontSize: 13,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    You don't have any venture showcases yet. Create a showcase first so sponsors can evaluate your problem, solution, and milestones.
                  </div>
                ) : (
                  <select
                    className="form-select"
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    required
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.title} ({p.stage} · {p.category})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Support Type */}
              <div className="form-group">
                <label className="form-label">Support Vehicle / Type *</label>
                <select
                  className="form-select"
                  value={sponsorshipType}
                  onChange={(e) => setSponsorshipType(e.target.value)}
                >
                  {SUPPORT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Monetary vs Non-Monetary Input */}
              {isMonetary ? (
                <div className="form-group">
                  <label className="form-label">Requested Allocation (₹ INR) *</label>
                  <input
                    type="number"
                    className="form-input"
                    value={proposedAmount}
                    onChange={(e) => setProposedAmount(e.target.value)}
                    min={1000}
                    step={1000}
                    required
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label className="form-label">Requested Resources & Specifications</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. 10 hours clinical advisory, 5x Jetson Orin boards, or $10k Cloud credits"
                    value={requestedResources}
                    onChange={(e) => setRequestedResources(e.target.value)}
                  />
                </div>
              )}

              {/* Pitch Message */}
              <div className="form-group">
                <label className="form-label">Introduction & Sponsorship Proposal *</label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder={`Explain why ${sponsor.organization_name || sponsor.full_name} is the ideal backing partner for your startup roadmap...`}
                  value={pitchMessage}
                  onChange={(e) => setPitchMessage(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                <Button variant="ghost" onClick={onClose} type="button">
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="emerald"
                  isLoading={isSubmitting}
                  disabled={projects.length === 0}
                >
                  Send Sponsorship Request →
                </Button>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 20 }}>
                You are currently signed in as a Sponsor or Guest. Only verified Entrepreneurs can propose venture sponsorship agreements.
              </p>
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
