import React, { useState } from 'react';
import { Button } from '../common/Button';

// Valid transitions mapping matching backend rules
const NEXT_TRANSITIONS = {
  interested: [
    { value: 'discussion', label: 'Move to Discussion', desc: 'Engage in scoping and terms exploration' },
    { value: 'cancelled', label: 'Cancel Commitment', desc: 'Terminate commitment record' },
  ],
  discussion: [
    { value: 'promised', label: 'Offer Term Sheet (Promised)', desc: 'Sponsor pledges formal support commitment' },
    { value: 'cancelled', label: 'Cancel Commitment', desc: 'Terminate commitment record' },
  ],
  promised: [
    { value: 'confirmed', label: 'Confirm Terms', desc: 'Both parties agree on terms and allocation' },
    { value: 'cancelled', label: 'Cancel Commitment', desc: 'Terminate commitment record' },
  ],
  confirmed: [
    { value: 'agreement', label: 'Sign Agreement', desc: 'Formal legal agreement executed' },
    { value: 'cancelled', label: 'Cancel Commitment', desc: 'Terminate commitment record' },
  ],
  agreement: [
    { value: 'funded', label: 'Disburse Funds / Deliver Resources', desc: 'Capital transferred or credits/hardware delivered' },
    { value: 'cancelled', label: 'Cancel Commitment', desc: 'Terminate commitment record' },
  ],
  funded: [
    { value: 'completed', label: 'Complete Commitment', desc: 'All obligations fulfilled & verified' },
  ],
  completed: [],
  cancelled: [],
};

export function StatusTransitionModal({ commitment, userRole, onClose, onUpdated }) {
  const currentStatus = commitment?.status || 'interested';
  const availableOptions = (NEXT_TRANSITIONS[currentStatus] || []).filter((opt) => {
    // Role guards matching backend:
    if (opt.value === 'promised' && userRole !== 'sponsor' && userRole !== 'admin') {
      return false;
    }
    if (opt.value === 'funded' && userRole !== 'sponsor' && userRole !== 'admin') {
      return false;
    }
    return true;
  });

  const [selectedStatus, setSelectedStatus] = useState(availableOptions[0]?.value || '');
  const [note, setNote] = useState('');
  const [agreementRef, setAgreementRef] = useState(commitment?.agreement_reference || '');
  const [followUpDate, setFollowUpDate] = useState('');
  const [followUpReason, setFollowUpReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const isCancelling = selectedStatus === 'cancelled';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedStatus) {
      setErrorMsg('Please choose a valid status to proceed.');
      return;
    }
    if (!note.trim()) {
      setErrorMsg(isCancelling ? 'A cancellation reason is required for audit history.' : 'Please add an explanatory note for this status update.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const payload = {
        new_status: selectedStatus,
        note: note.trim(),
      };
      if (followUpDate) {
        payload.follow_up_date = new Date(followUpDate).toISOString();
      }
      if (followUpReason.trim()) {
        payload.follow_up_reason = followUpReason.trim();
      }
      if (agreementRef.trim()) {
        payload.agreement_reference = agreementRef.trim();
      }

      await onUpdated(payload);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update commitment status.');
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
        zIndex: 300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
      }}
    >
      <div className="card" style={{ maxWidth: 520, width: '100%', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>
              Advance Commitment Lifecycle
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Current Status: <strong style={{ color: 'var(--brand-cyan)' }}>{currentStatus.toUpperCase()}</strong>
            </p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>

        {errorMsg && (
          <div className="alert alert-error" style={{ marginBottom: 16 }}>
            <span>{errorMsg}</span>
          </div>
        )}

        {availableOptions.length === 0 ? (
          <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No further status transitions are available from the current stage.
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {/* Target Status Selection */}
            <div className="form-group">
              <label className="form-label">Next Lifecycle Stage *</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {availableOptions.map((opt) => (
                  <label
                    key={opt.value}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      padding: 12,
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: selectedStatus === opt.value
                        ? opt.value === 'cancelled'
                          ? 'rgba(244, 63, 94, 0.12)'
                          : 'rgba(6, 182, 212, 0.12)'
                        : 'rgba(18, 25, 39, 0.6)',
                      border: selectedStatus === opt.value
                        ? `1px solid ${opt.value === 'cancelled' ? 'var(--brand-rose)' : 'var(--brand-cyan)'}`
                        : '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                    }}
                  >
                    <input
                      type="radio"
                      name="target_status"
                      value={opt.value}
                      checked={selectedStatus === opt.value}
                      onChange={(e) => setSelectedStatus(e.target.value)}
                      style={{ marginTop: 3 }}
                    />
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: opt.value === 'cancelled' ? 'var(--brand-rose)' : 'var(--text-primary)' }}>
                        {opt.label}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                        {opt.desc}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Note / Audit Reason */}
            <div className="form-group">
              <label className="form-label">
                {isCancelling ? 'Reason for Cancellation *' : 'Milestone Transition Note *'}
              </label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder={
                  isCancelling
                    ? 'Explain why this commitment is being cancelled for platform audit logs...'
                    : 'Detail the decisions, signed terms, or disbursement context for this stage...'
                }
                value={note}
                onChange={(e) => setNote(e.target.value)}
                required
              />
            </div>

            {/* Conditional: Agreement Reference */}
            {(selectedStatus === 'agreement' || currentStatus === 'agreement') && (
              <div className="form-group">
                <label className="form-label">Agreement Reference / Contract ID</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. VYNK-SPON-2026-081"
                  value={agreementRef}
                  onChange={(e) => setAgreementRef(e.target.value)}
                />
              </div>
            )}

            {/* Follow-up reminder */}
            {!isCancelling && selectedStatus !== 'completed' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                <div className="form-group">
                  <label className="form-label">Next Follow-Up Date</label>
                  <input
                    type="date"
                    className="form-input"
                    value={followUpDate}
                    onChange={(e) => setFollowUpDate(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Follow-Up Goal / Reason</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Review pilot metrics"
                    value={followUpReason}
                    onChange={(e) => setFollowUpReason(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
              <Button variant="ghost" onClick={onClose} type="button">
                Cancel
              </Button>
              <Button
                type="submit"
                variant={isCancelling ? 'danger' : 'emerald'}
                isLoading={isSubmitting}
              >
                {isCancelling ? 'Confirm Cancellation' : 'Confirm & Update Stage →'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
