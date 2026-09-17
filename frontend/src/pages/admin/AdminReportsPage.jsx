import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export function AdminReportsPage() {
  const [reports, setReports] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Filter
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Resolution Modal
  const [selectedReport, setSelectedReport] = useState(null);
  const [targetStatus, setTargetStatus] = useState('resolved');
  const [resolutionNote, setResolutionNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadReports();
  }, [page, statusFilter, categoryFilter]);

  const loadReports = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = {
        page,
        limit,
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
      };
      const res = await adminService.getAdminReports(params);
      setReports(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load reports:', err);
      setError(err.message || 'Failed to fetch reports queue');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!selectedReport) return;

    try {
      setIsSubmitting(true);
      setError(null);
      await adminService.reviewReport(selectedReport.id, {
        status: targetStatus,
        resolution_note: resolutionNote.trim() || undefined,
      });
      setSuccessMessage(`Report #${selectedReport.id.slice(0, 8)} marked as ${targetStatus}.`);
      setSelectedReport(null);
      setResolutionNote('');
      loadReports();
    } catch (err) {
      console.error('Report review failed:', err);
      setError(err.message || 'Report review failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>Content & User Reports Queue</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Investigate community flags for spam, fraud, harassment, and unacceptable platform conduct.
          </p>
        </div>
        <Badge variant="rose">{total} Reports Logged</Badge>
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
          <div style={{ flex: '0 1 200px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Status: All</option>
              <option value="pending">Pending</option>
              <option value="reviewed">Reviewed</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>

          <div style={{ flex: '0 1 200px' }}>
            <select
              className="form-select"
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Category: All</option>
              <option value="spam">Spam</option>
              <option value="fraud">Fraud</option>
              <option value="harassment">Harassment</option>
              <option value="inappropriate_content">Inappropriate Content</option>
              <option value="copyright_violation">Copyright Violation</option>
              <option value="other">Other</option>
            </select>
          </div>

          {(statusFilter || categoryFilter) && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setStatusFilter('');
                setCategoryFilter('');
                setPage(1);
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Reports Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} />
          </div>
        ) : reports.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No reports in this queue.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ backgroundColor: 'rgba(13, 18, 29, 0.7)', borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '14px 16px' }}>Date</th>
                  <th style={{ padding: '14px 16px' }}>Reporter</th>
                  <th style={{ padding: '14px 16px' }}>Reported Target</th>
                  <th style={{ padding: '14px 16px' }}>Category</th>
                  <th style={{ padding: '14px 16px' }}>Reason / Notes</th>
                  <th style={{ padding: '14px 16px' }}>Status</th>
                  <th style={{ padding: '14px 16px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => {
                  let targetLabel = 'Entity';
                  if (r.reported_user_id) targetLabel = `User #${r.reported_user_id.slice(0, 8)}`;
                  else if (r.reported_project_id) targetLabel = `Project #${r.reported_project_id.slice(0, 8)}`;
                  else if (r.reported_commitment_id) targetLabel = `Commitment #${r.reported_commitment_id.slice(0, 8)}`;
                  else if (r.reported_sponsorship_request_id) targetLabel = `Request #${r.reported_sponsorship_request_id.slice(0, 8)}`;

                  return (
                    <tr key={r.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                        {new Date(r.created_at).toLocaleDateString()}
                      </td>

                      <td style={{ padding: '14px 16px' }}>
                        {r.reporter ? (
                          <div>
                            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{r.reporter.full_name}</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.reporter.email}</div>
                          </div>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>User #{r.reporter_id.slice(0, 8)}</span>
                        )}
                      </td>

                      <td style={{ padding: '14px 16px', fontWeight: 500, color: 'var(--brand-cyan)' }}>
                        {targetLabel}
                      </td>

                      <td style={{ padding: '14px 16px' }}>
                        <Badge variant={r.category === 'fraud' || r.category === 'harassment' ? 'rose' : 'amber'}>
                          {r.category || 'general'}
                        </Badge>
                      </td>

                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', maxWidth: 260 }}>
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.reason || r.description}>
                          {r.reason || r.description || '—'}
                        </div>
                        {r.resolution_note && (
                          <div style={{ fontSize: 11, color: 'var(--brand-emerald)', marginTop: 2 }}>
                            Resolution: {r.resolution_note}
                          </div>
                        )}
                      </td>

                      <td style={{ padding: '14px 16px' }}>
                        <Badge
                          variant={
                            r.status === 'resolved'
                              ? 'emerald'
                              : r.status === 'dismissed'
                              ? 'secondary'
                              : 'rose'
                          }
                        >
                          {r.status}
                        </Badge>
                      </td>

                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => {
                            setSelectedReport(r);
                            setTargetStatus(r.status === 'pending' ? 'resolved' : r.status);
                            setResolutionNote(r.resolution_note || '');
                          }}
                        >
                          Review
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {total > limit && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} reports
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

      {/* Review Modal */}
      {selectedReport && (
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
          <div className="card" style={{ maxWidth: 520, width: '100%', backgroundColor: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>Review Report #{selectedReport.id.slice(0, 8)}</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
              Category: <Badge variant="amber">{selectedReport.category}</Badge>
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
              <div style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: 4 }}>Report Content:</div>
              {selectedReport.description || selectedReport.reason || 'No description provided.'}
            </div>

            <form onSubmit={handleReviewSubmit}>
              <div className="form-group">
                <label className="form-label">Update Status</label>
                <select className="form-select" value={targetStatus} onChange={(e) => setTargetStatus(e.target.value)}>
                  <option value="resolved">Mark as Resolved (Action taken)</option>
                  <option value="dismissed">Dismiss (No violation)</option>
                  <option value="reviewed">Keep Under Review</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Resolution Note (Optional)</label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder="Record findings and outcome for audit trail..."
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
                <Button variant="secondary" size="sm" onClick={() => setSelectedReport(null)} disabled={isSubmitting}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
                  Save Resolution
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminReportsPage;
