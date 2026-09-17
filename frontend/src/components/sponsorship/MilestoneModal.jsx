import React, { useState } from 'react';
import { Button } from '../common/Button';

export function MilestoneModal({ commitmentId, onClose, onAdded }) {
  const [title, setTitle] = useState('');
  const [note, setNote] = useState('');
  const [updateType, setUpdateType] = useState('milestone');
  const [evidenceRef, setEvidenceRef] = useState('');
  const [eventDate, setEventDate] = useState(new Date().toISOString().split('T')[0]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !note.trim()) {
      setErrorMsg('Please enter both a title and descriptive note for this update.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const payload = {
        title: title.trim(),
        note: note.trim(),
        update_type: updateType,
        evidence_reference: evidenceRef.trim() || undefined,
        event_date: eventDate ? new Date(eventDate).toISOString() : undefined,
      };
      await onAdded(payload);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to post milestone update.');
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
      <div className="card" style={{ maxWidth: 500, width: '100%', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>Record Progress Update</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Log milestone completion, resource delivery, or notes against this commitment.
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

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Update Type / Category *</label>
            <select
              className="form-select"
              value={updateType}
              onChange={(e) => setUpdateType(e.target.value)}
            >
              <option value="milestone">Milestone Achieved</option>
              <option value="resource_delivered">Resource / Hardware Delivered</option>
              <option value="credits_issued">Credits / Software Activated</option>
              <option value="fund_transfer">Capital / Tranche Disbursed</option>
              <option value="mentoring_session">Mentoring / Advisory Held</option>
              <option value="agreement_signed">Agreement Signed / Executed</option>
              <option value="note">General Note / Check-in</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Update Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. AWS $25,000 Cloud Credits Activated"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description & Evidence Details *</label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="Describe what was delivered, verified, or discussed in this step..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 14 }}>
            <div className="form-group">
              <label className="form-label">Evidence / Reference URL (optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. https://... or Ref# UTR-998"
                value={evidenceRef}
                onChange={(e) => setEvidenceRef(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Event Date</label>
              <input
                type="date"
                className="form-input"
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
            <Button variant="ghost" onClick={onClose} type="button">
              Cancel
            </Button>
            <Button type="submit" variant="emerald" isLoading={isSubmitting}>
              Add Update +
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
