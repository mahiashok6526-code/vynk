import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export function AdminDisputesPage() {
  const [disputes, setDisputes] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Filter
  const [statusFilter, setStatusFilter] = useState('');

  // Arbitration Modal
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [targetStatus, setTargetStatus] = useState('resolved');
  const [resolutionNote, setResolutionNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadDisputes();
  }, [page, statusFilter]);

  const loadDisputes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = {
        page,
        limit,
        status: statusFilter || undefined,
      };
      const res = await adminService.getAdminDisputes(params);
      setDisputes(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load disputes:', err);
      setError(err.message || 'Failed to fetch dispute queue');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDispute) return;

    try {
      setIsSubmitting(true);
      setError(null);
      await adminService.reviewDispute(selectedDispute.id, {
        status: targetStatus,
        resolution_note: resolutionNote.trim() || undefined,
      });
      setSuccessMessage(`Dispute #${selectedDispute.id.slice(0, 8)} updated to ${targetStatus}.`);
      setSelectedDispute(null);
      setResolutionNote('');
      loadDisputes();
    } catch (err) {
      console.error('Dispute arbitration failed:', err);
      setError(err.message || 'Dispute arbitration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>Sponsorship Dispute Arbitration</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Fair third-party mediation for milestone delivery breaches, non-payment, and sponsorship disagreements.
          </p>
        </div>
        <Badge variant="indigo">{total} Disputes Tracked</Badge>
      </div>

      {successMessage && (
        <div className="alert alert-success" style={{ marginBottom: 20 }}>
          <span>✓</span>
          <span style={{ flex: 1 }}>{successMessage}</span>
          <button onClick={() => setSuccessMessage(null)} className="btn btn-ghost btn-sm" style={{ padding: '2px 8px' }}>
            ✕
          </button>
        </div>
      )}

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 20 }}>
          <span>⚠</span>
          <span style={{ flex: 1 }}>{error}</span>
          <button onClick={() => setError(null)} className="btn btn-ghost btn-sm" style={{ padding: '2px 8px' }}>
            ✕
          </button>
        </div>
      )}

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: 24, padding: 18 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: '0 1 220px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Status: All</option>
              <option value="opened">Opened</option>
              <option value="under_review">Under Review</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>

          {statusFilter && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setStatusFilter('');
                setPage(1);
              }}
            >
              Clear Filter
            </button>
          )}
        </div>
      </div>

      {/* Disputes Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} />
          </div>
        ) : disputes.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No disputes found in this queue.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ backgroundColor: 'rgba(13, 18, 29, 0.7)', borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '14px 16px' }}>Opened</th>
                  <th style={{ padding: '14px 16px' }}>Parties</th>
                  <th style={{ padding: '14px 16px' }}>Target Context</th>
                  <th style={{ padding: '14px 16px' }}>Dispute Reason</th>
                  <th style={{ padding: '14px 16px' }}>Description / Finding</th>
                  <th style={{ padding: '14px 16px' }}>Status</th>
                  <th style={{ padding: '14px 16px', textAlign: 'right' }}>Arbitrate</th>
                </tr>
              </thead>
              <tbody>
                {disputes.map((d) => (
                  <tr key={d.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(d.created_at).toLocaleDateString()}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {d.initiator ? d.initiator.full_name : `#${d.initiator_id.slice(0, 8)}`}
                      </div>
                      {d.against_user && (
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                          vs. {d.against_user.full_name}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px', color: 'var(--brand-cyan)' }}>
                      {d.commitment_id
                        ? `Commitment #${d.commitment_id.slice(0, 8)}`
                        : d.sponsorship_request_id
                        ? `Request #${d.sponsorship_request_id.slice(0, 8)}`
                        : 'General Agreement'}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <Badge variant="indigo">{d.reason}</Badge>
                    </td>

                    <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', maxWidth: 260 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={d.description}>
                        {d.description}
                      </div>
                      {d.resolution_note && (
                        <div style={{ fontSize: 11, color: 'var(--brand-emerald)', marginTop: 2 }}>
                          Resolution: {d.resolution_note}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <Badge
                        variant={
                          d.status === 'resolved'
                            ? 'emerald'
                            : d.status === 'dismissed'
                            ? 'secondary'
                            : d.status === 'under_review'
                            ? 'cyan'
                            : 'amber'
                        }
                      >
                        {d.status}
                      </Badge>
                    </td>

                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => {
                          setSelectedDispute(d);
                          setTargetStatus(d.status === 'opened' ? 'under_review' : d.status);
                          setResolutionNote(d.resolution_note || '');
                        }}
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {total > limit && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} disputes
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Previous
              </button>
              <button className="btn btn-secondary btn-sm" disabled={page * limit >= total} onClick={() => setPage((p) => p + 1)}>
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Arbitration Modal */}
      {selectedDispute && (
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
            zIndex: 1000,
            padding: 20,
          }}
        >
          <div className="card" style={{ maxWidth: 540, width: '100%', backgroundColor: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>Arbitrate Dispute #{selectedDispute.id.slice(0, 8)}</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
              Reason: <Badge variant="indigo">{selectedDispute.reason}</Badge>
            </p>

            <div
              style={{
                backgroundColor: 'rgba(7, 9, 14, 0.6)',
                padding: 16,
                borderRadius: 'var(--radius-md)',
                marginBottom: 20,
                fontSize: 13,
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
              }}
            >
              <div style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: 4 }}>Dispute Claim:</div>
              {selectedDispute.description}
            </div>

            <form onSubmit={handleReviewSubmit}>
              <div className="form-group">
                <label className="form-label">Arbitration Status</label>
                <select className="form-select" value={targetStatus} onChange={(e) => setTargetStatus(e.target.value)}>
                  <option value="under_review">Mark Under Review</option>
                  <option value="resolved">Resolve Dispute (Remedy agreed)</option>
                  <option value="dismissed">Dismiss Dispute (Unsubstantiated)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Arbitration Note (Required for resolution/dismissal)</label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder="Summarize agreed remedy or arbitration decision..."
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
                <Button variant="secondary" size="sm" onClick={() => setSelectedDispute(null)} disabled={isSubmitting}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
                  Save Arbitration
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDisputesPage;
