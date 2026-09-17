import React, { useState } from 'react';
import { adminService } from '../../services/adminService';
import { Button } from './Button';

export function ReportModal({
  isOpen,
  onClose,
  targetType = 'user', // 'user' | 'project' | 'commitment' | 'sponsorship_request'
  targetId,
  targetTitle = '',
}) {
  const [category, setCategory] = useState('spam');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Please provide a description of the issue.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const payload = {
        category,
        description: description.trim(),
      };

      if (targetType === 'user') payload.reported_user_id = targetId;
      else if (targetType === 'project') payload.reported_project_id = targetId;
      else if (targetType === 'commitment') payload.reported_commitment_id = targetId;
      else if (targetType === 'sponsorship_request') payload.reported_sponsorship_request_id = targetId;

      await adminService.submitReport(payload);
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        setDescription('');
        onClose();
      }, 1500);
    } catch (err) {
      console.error('Failed to submit report:', err);
      setError(err.message || 'Failed to submit report. Please try again.');
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
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(7, 9, 14, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
        padding: 20,
      }}
    >
      <div className="card" style={{ maxWidth: 460, width: '100%', backgroundColor: 'var(--bg-surface)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ fontSize: 18, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>⚠️</span> Report {targetType.charAt(0).toUpperCase() + targetType.slice(1)}
          </h3>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm"
            style={{ padding: '4px 8px', color: 'var(--text-muted)' }}
          >
            ✕
          </button>
        </div>

        {targetTitle && (
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Reporting: <strong style={{ color: 'var(--text-primary)' }}>{targetTitle}</strong>
          </div>
        )}

        {isSuccess ? (
          <div style={{ padding: '24px 0', textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>✓</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--brand-emerald)', marginBottom: 4 }}>
              Report Submitted
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Thank you. Our moderation team has received your report for review.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {error && (
              <div className="alert alert-error" style={{ padding: '10px 14px', fontSize: 13, marginBottom: 14 }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Category</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="spam">Spam or Unsolicited Promotion</option>
                <option value="fraud">Suspected Fraud or Scam</option>
                <option value="harassment">Harassment or Abusive Conduct</option>
                <option value="inappropriate_content">Inappropriate / Harmful Content</option>
                <option value="copyright_violation">Intellectual Property Infringement</option>
                <option value="other">Other Violation</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Description & Evidence</label>
              <textarea
                className="form-textarea"
                rows={4}
                placeholder="Describe what occurred and why this violates Vynk platform policies..."
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
              <Button variant="secondary" size="sm" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button
                variant="secondary"
                size="sm"
                type="submit"
                style={{ color: 'var(--brand-rose)', borderColor: 'var(--brand-rose)' }}
                isLoading={isSubmitting}
              >
                Submit Report
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default ReportModal;
