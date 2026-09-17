import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { VynkLogo } from '../../components/common/VynkLogo';
import { CommitmentTimeline } from '../../components/sponsorship/CommitmentTimeline';
import { StatusTransitionModal } from '../../components/sponsorship/StatusTransitionModal';
import { MilestoneModal } from '../../components/sponsorship/MilestoneModal';
import { formatCurrency } from '../../utils/currency';

export function CommitmentDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [commitment, setCommitment] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [isTransitionOpen, setIsTransitionOpen] = useState(false);
  const [isMilestoneOpen, setIsMilestoneOpen] = useState(false);
  const [successToast, setSuccessToast] = useState('');

  const loadCommitment = async () => {
    try {
      const data = await apiRequest(`/commitments/${id}`);
      setCommitment(data);
    } catch (err) {
      console.error('Error loading commitment:', err);
      setErrorMsg(err.message || 'Commitment not found or unauthorized.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCommitment();
  }, [id]);

  const handleStatusUpdate = async (payload) => {
    await apiRequest(`/commitments/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    setSuccessToast(`Commitment advanced to "${payload.new_status}"!`);
    setTimeout(() => setSuccessToast(''), 4000);
    await loadCommitment();
  };

  const handleMilestoneAdded = async (payload) => {
    await apiRequest(`/commitments/${id}/updates`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    setSuccessToast('Milestone update recorded successfully!');
    setTimeout(() => setSuccessToast(''), 4000);
    await loadCommitment();
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 36, height: 36 }} />
      </div>
    );
  }

  if (errorMsg || !commitment) {
    return (
      <div className="section container" style={{ paddingTop: 60, textAlign: 'center' }}>
        <div className="card" style={{ maxWidth: 500, margin: '0 auto' }}>
          <h2 style={{ fontSize: 22, color: 'var(--brand-rose)', marginBottom: 12 }}>Commitment Access Notice</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
            {errorMsg || 'The requested commitment record does not exist or you lack authorization to view it.'}
          </p>
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>
            ← Return to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const isTerminal = commitment.status === 'completed' || commitment.status === 'cancelled';
  const isMonetary = (commitment.amount || 0) > 0;

  return (
    <div className="section" style={{ paddingTop: 24, minHeight: '85vh' }}>
      <div className="container">
        {/* Breadcrumb Navigation */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          <Link to="/dashboard" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
            Dashboard
          </Link>
          <span>/</span>
          <span style={{ color: 'var(--text-primary)' }}>Commitment #{commitment.id}</span>
        </div>

        {successToast && (
          <div className="alert alert-success" style={{ marginBottom: 20 }}>
            <span>{successToast}</span>
          </div>
        )}

        {/* Overdue Alert Banner */}
        {commitment.is_overdue && (
          <div
            style={{
              padding: '14px 18px',
              backgroundColor: 'rgba(244, 63, 94, 0.12)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              borderRadius: 'var(--radius-md)',
              marginBottom: 24,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: 'var(--brand-rose)', fontSize: 18 }}>⏱</span>
              <div>
                <strong style={{ color: 'var(--brand-rose)', fontSize: 14 }}>Follow-up Due / Overdue</strong>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                  {commitment.follow_up_reason || 'Target milestone follow-up is pending.'} (Due: {new Date(commitment.follow_up_date).toLocaleDateString()})
                </div>
              </div>
            </div>
            {!isTerminal && (
              <Button size="sm" variant="secondary" onClick={() => setIsTransitionOpen(true)}>
                Update Status / Reschedule
              </Button>
            )}
          </div>
        )}

        {/* Main Header Card */}
        <div
          className="card"
          style={{
            marginBottom: 28,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(6, 182, 212, 0.05) 100%)',
            border: '1px solid var(--border-medium)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <VynkLogo variant="symbol" size={22} />
                <Badge variant="cyan">{commitment.sponsorship_type}</Badge>
                <Badge
                  variant={
                    commitment.status === 'completed'
                      ? 'emerald'
                      : commitment.status === 'cancelled'
                      ? 'rose'
                      : commitment.status === 'agreement' || commitment.status === 'funded'
                      ? 'indigo'
                      : 'amber'
                  }
                >
                  {commitment.status.toUpperCase()}
                </Badge>
              </div>

              <h1 style={{ fontSize: 26, marginBottom: 6 }}>
                {commitment.title || `${commitment.sponsorship_type} Commitment`}
              </h1>

              {commitment.project_title && (
                <p style={{ fontSize: 15, color: 'var(--text-secondary)' }}>
                  Venture Showcase:{' '}
                  <Link
                    to={`/projects/${commitment.project_id}`}
                    style={{ color: 'var(--brand-cyan)', fontWeight: 600, textDecoration: 'none' }}
                  >
                    {commitment.project_title} →
                  </Link>
                </p>
              )}
            </div>

            {/* Quick Actions */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              <Button variant="secondary" size="sm" onClick={() => setIsMilestoneOpen(true)}>
                + Add Milestone Update
              </Button>
              {!isTerminal && (
                <Button variant="emerald" size="sm" onClick={() => setIsTransitionOpen(true)}>
                  Advance Stage →
                </Button>
              )}
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
            <div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Support Allocation
              </span>
              <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--brand-emerald)', marginTop: 4 }}>
                {isMonetary ? formatCurrency(commitment.amount, commitment.currency || 'INR') : 'Non-Monetary'}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                Currency: {commitment.currency || 'INR'}
              </div>
            </div>

            <div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Sponsor Partner
              </span>
              <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>
                {commitment.sponsor_name || 'Verified Sponsor'}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                {commitment.sponsor_org || 'Independent Angel'}
              </div>
            </div>

            <div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Entrepreneur / Founder
              </span>
              <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>
                {commitment.entrepreneur_name || 'Venture Founder'}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                Project Lead
              </div>
            </div>

            <div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Agreement Reference
              </span>
              <div style={{ fontSize: 14, fontWeight: 600, color: commitment.agreement_reference ? 'var(--brand-cyan)' : 'var(--text-muted)', marginTop: 4 }}>
                {commitment.agreement_reference || 'Pending Execution'}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                Initiated: {new Date(commitment.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          {commitment.description && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border-subtle)', fontSize: 14, color: 'var(--text-secondary)' }}>
              <strong>Scope & Objectives:</strong> {commitment.description}
            </div>
          )}
        </div>

        {/* 7-Stage Lifecycle Timeline */}
        <div style={{ marginBottom: 32 }}>
          <CommitmentTimeline currentStatus={commitment.status} />
        </div>

        {/* Audit Log & Progress Milestones Stream */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700 }}>Milestone Updates & Audit Stream</h3>
              <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                Auditable chronological timeline of status changes, delivered assets, and milestones.
              </p>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setIsMilestoneOpen(true)}>
              + Log Update
            </Button>
          </div>

          {(!commitment.updates || commitment.updates.length === 0) ? (
            <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No updates logged yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16, position: 'relative' }}>
              {commitment.updates.map((upd) => (
                <div
                  key={upd.id}
                  style={{
                    display: 'flex',
                    gap: 16,
                    padding: 16,
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'rgba(7, 9, 14, 0.65)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  {/* Icon Indicator */}
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: '50%',
                      backgroundColor: upd.update_type === 'status_change' ? 'rgba(6, 182, 212, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                      border: `1px solid ${upd.update_type === 'status_change' ? 'var(--brand-cyan)' : 'var(--brand-emerald)'}`,
                      color: upd.update_type === 'status_change' ? 'var(--brand-cyan)' : 'var(--brand-emerald)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 16,
                      flexShrink: 0,
                    }}
                  >
                    {upd.update_type === 'status_change' ? '⟳' : '★'}
                  </div>

                  {/* Body */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 4 }}>
                      <div>
                        <strong style={{ fontSize: 15, color: 'var(--text-primary)' }}>
                          {upd.title || upd.update_type.replace('_', ' ').toUpperCase()}
                        </strong>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
                          by {upd.updater_name || 'Participant'} ({upd.updater_role || 'member'})
                        </span>
                      </div>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        {new Date(upd.created_at).toLocaleString()}
                      </span>
                    </div>

                    <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 4, lineHeight: 1.5 }}>
                      {upd.note}
                    </p>

                    {upd.evidence_reference && (
                      <div style={{ marginTop: 8, fontSize: 12 }}>
                        <span style={{ color: 'var(--text-muted)' }}>Evidence / Ref: </span>
                        {upd.evidence_reference.startsWith('http') ? (
                          <a
                            href={upd.evidence_reference}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: 'var(--brand-cyan)', textDecoration: 'underline' }}
                          >
                            {upd.evidence_reference}
                          </a>
                        ) : (
                          <code style={{ padding: '2px 6px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: 4 }}>
                            {upd.evidence_reference}
                          </code>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modals */}
        {isTransitionOpen && (
          <StatusTransitionModal
            commitment={commitment}
            userRole={user?.role}
            onClose={() => setIsTransitionOpen(false)}
            onUpdated={handleStatusUpdate}
          />
        )}

        {isMilestoneOpen && (
          <MilestoneModal
            commitmentId={commitment.id}
            onClose={() => setIsMilestoneOpen(false)}
            onAdded={handleMilestoneAdded}
          />
        )}
      </div>
    </div>
  );
}
