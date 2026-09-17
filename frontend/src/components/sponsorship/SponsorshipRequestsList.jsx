import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { formatCurrency } from '../../utils/currency';
import { apiRequest } from '../../services/api';

export function SponsorshipRequestsList({ requests = [], userRole, onRefresh }) {
  const [respondingReq, setRespondingReq] = useState(null); // { req, action: 'accept' | 'reject' }
  const [responseNote, setResponseNote] = useState('');
  const [customAmount, setCustomAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const isEntrepreneur = userRole === 'entrepreneur';

  const handleCancelRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to cancel this sponsorship request?')) return;
    try {
      await apiRequest(`/sponsorship-requests/${requestId}/cancel`, { method: 'POST' });
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(err.message || 'Failed to cancel request.');
    }
  };

  const handleOpenRespond = (req, action) => {
    setRespondingReq({ req, action });
    setResponseNote('');
    setCustomAmount(req.requested_amount || '');
    setErrorMsg('');
  };

  const handleConfirmRespond = async (e) => {
    e.preventDefault();
    if (!respondingReq) return;
    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const payload = {
        action: respondingReq.action,
        response_note: responseNote.trim() || undefined,
      };
      if (respondingReq.action === 'accept' && customAmount) {
        payload.commitment_amount = Number(customAmount);
      }

      await apiRequest(`/sponsorship-requests/${respondingReq.req.id}/respond`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setRespondingReq(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process request response.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (requests.length === 0) {
    return (
      <div
        style={{
          padding: '36px 16px',
          textAlign: 'center',
          backgroundColor: 'rgba(7, 9, 14, 0.5)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>
          {isEntrepreneur ? 'No sponsorship requests sent yet.' : 'No incoming sponsorship requests at this time.'}
        </p>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
          {isEntrepreneur
            ? 'Browse verified sponsors or explore AI recommendations to propose a venture backing request.'
            : 'When entrepreneurs propose sponsorship for their venture showcases, their requests will appear here.'}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {requests.map((r) => {
        const isPending = r.status === 'pending';
        const isAccepted = r.status === 'accepted';
        const isRejected = r.status === 'rejected';

        return (
          <div
            key={r.id}
            style={{
              padding: 16,
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(7, 9, 14, 0.7)',
              border: isPending
                ? '1px solid rgba(6, 182, 212, 0.3)'
                : '1px solid var(--border-subtle)',
            }}
          >
            {/* Header row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 10, marginBottom: 10 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <Badge variant="cyan">{r.sponsorship_type}</Badge>
                  <Badge
                    variant={
                      isAccepted
                        ? 'emerald'
                        : isRejected
                        ? 'rose'
                        : isPending
                        ? 'amber'
                        : 'secondary'
                    }
                  >
                    {r.status.toUpperCase()}
                  </Badge>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    #{r.id} · {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h4 style={{ fontSize: 16, fontWeight: 700 }}>
                  {r.project?.title ? (
                    <Link to={`/projects/${r.project_id}`} style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>
                      {r.project.title}
                    </Link>
                  ) : (
                    `Project #${r.project_id}`
                  )}
                </h4>
              </div>

              {/* Counterparty badge */}
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  {isEntrepreneur ? 'Target Sponsor' : 'Entrepreneur Lead'}
                </span>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {isEntrepreneur
                    ? r.recipient?.organization_name || r.recipient?.full_name || 'Sponsor'
                    : r.sender?.full_name || 'Entrepreneur'}
                </div>
              </div>
            </div>

            {/* Support Details */}
            <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', padding: '8px 12px', background: 'rgba(18, 25, 39, 0.5)', borderRadius: 'var(--radius-sm)', marginBottom: 12 }}>
              <div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Requested Support: </span>
                <strong style={{ fontSize: 13, color: 'var(--brand-emerald)' }}>
                  {r.requested_amount
                    ? formatCurrency(r.requested_amount, r.currency || 'INR')
                    : 'Non-Monetary'}
                </strong>
              </div>

              {r.requested_resources && (
                <div>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Resources: </span>
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{r.requested_resources}</span>
                </div>
              )}
            </div>

            {/* Pitch / Message */}
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.5 }}>
              "{r.message}"
            </p>

            {/* Response Note (if any) */}
            {r.response_note && (
              <div
                style={{
                  padding: 10,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isAccepted ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
                  border: isAccepted ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid rgba(244, 63, 94, 0.2)',
                  fontSize: 12,
                  color: isAccepted ? 'var(--brand-emerald)' : 'var(--brand-rose)',
                  marginBottom: 12,
                }}
              >
                <strong>Sponsor Response:</strong> {r.response_note}
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, alignItems: 'center' }}>
              {isAccepted && r.commitment_id && (
                <Link to={`/commitments/${r.commitment_id}`} style={{ textDecoration: 'none' }}>
                  <Button size="sm" variant="emerald">
                    View Active Commitment #{r.commitment_id} →
                  </Button>
                </Link>
              )}

              {isEntrepreneur && isPending && (
                <Button size="sm" variant="ghost" onClick={() => handleCancelRequest(r.id)}>
                  Cancel Request
                </Button>
              )}

              {!isEntrepreneur && isPending && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <Button size="sm" variant="secondary" onClick={() => handleOpenRespond(r, 'reject')}>
                    Decline
                  </Button>
                  <Button size="sm" variant="emerald" onClick={() => handleOpenRespond(r, 'accept')}>
                    Accept & Commit →
                  </Button>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Mini Response Modal for Sponsors */}
      {respondingReq && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(7, 9, 14, 0.85)',
            backdropFilter: 'blur(8px)',
            zIndex: 350,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 20,
          }}
        >
          <div className="card" style={{ maxWidth: 460, width: '100%', border: '1px solid var(--border-glow)' }}>
            <h3 style={{ fontSize: 18, marginBottom: 6 }}>
              {respondingReq.action === 'accept' ? 'Accept Sponsorship Request' : 'Decline Request'}
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
              {respondingReq.action === 'accept'
                ? 'Accepting creates a structured commitment record in INTERESTED status in your portfolio pipeline.'
                : 'Decline this proposal with an optional polite note to the entrepreneur.'}
            </p>

            {errorMsg && (
              <div className="alert alert-error" style={{ marginBottom: 14 }}>
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleConfirmRespond}>
              {respondingReq.action === 'accept' && respondingReq.req.requested_amount && (
                <div className="form-group">
                  <label className="form-label">Approved Allocation (₹ INR)</label>
                  <input
                    type="number"
                    className="form-input"
                    value={customAmount}
                    onChange={(e) => setCustomAmount(e.target.value)}
                    min={0}
                    step={1000}
                  />
                </div>
              )}

              <div className="form-group">
                <label className="form-label">
                  {respondingReq.action === 'accept' ? 'Welcome / Kickoff Note' : 'Decline Reason / Feedback'}
                </label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder={
                    respondingReq.action === 'accept'
                      ? 'Excited to back your roadmap! Let us schedule a kickoff call...'
                      : 'Thank you for pitching. Unfortunately, this does not fit our current thesis...'
                  }
                  value={responseNote}
                  onChange={(e) => setResponseNote(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 18 }}>
                <Button variant="ghost" onClick={() => setRespondingReq(null)} type="button">
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant={respondingReq.action === 'accept' ? 'emerald' : 'danger'}
                  isLoading={isSubmitting}
                >
                  {respondingReq.action === 'accept' ? 'Confirm Acceptance →' : 'Confirm Decline'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
