import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export function AdminProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Filters
  const [moderationStatus, setModerationStatus] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Review Modal
  const [selectedProject, setSelectedProject] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reviewMode, setReviewMode] = useState('view'); // 'view' | 'reject'

  useEffect(() => {
    loadProjects();
  }, [page, moderationStatus, statusFilter]);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = {
        page,
        limit,
        moderation_status: moderationStatus || undefined,
        status: statusFilter || undefined,
      };
      const res = await adminService.getAdminProjects(params);
      setProjects(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError(err.message || 'Failed to fetch project list');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (projectId) => {
    try {
      setIsSubmitting(true);
      setError(null);
      await adminService.approveProject(projectId);
      setSuccessMessage('Project approved successfully and notifications dispatched.');
      setSelectedProject(null);
      loadProjects();
    } catch (err) {
      console.error('Approval failed:', err);
      setError(err.message || 'Approval failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    if (!rejectionReason.trim()) {
      setError('Rejection reason is required to notify the entrepreneur.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await adminService.rejectProject(selectedProject.id, { reason: rejectionReason.trim() });
      setSuccessMessage('Project rejected and feedback notification sent to the founder.');
      setSelectedProject(null);
      setRejectionReason('');
      loadProjects();
    } catch (err) {
      console.error('Rejection failed:', err);
      setError(err.message || 'Rejection failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>Startup Showcase Moderation</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Review startup listings, verify showcase quality, approve discovery publication, or provide rejection feedback.
          </p>
        </div>
        <Badge variant="cyan">{total} Projects Tracked</Badge>
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
              value={moderationStatus}
              onChange={(e) => {
                setModerationStatus(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Moderation: All</option>
              <option value="pending_review">Pending Review</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div style={{ flex: '0 1 200px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Lifecycle: All</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          {(moderationStatus || statusFilter) && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setModerationStatus('');
                setStatusFilter('');
                setPage(1);
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Projects Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} />
          </div>
        ) : projects.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No projects in this queue.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ backgroundColor: 'rgba(13, 18, 29, 0.7)', borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '14px 16px' }}>Project</th>
                  <th style={{ padding: '14px 16px' }}>Founder</th>
                  <th style={{ padding: '14px 16px' }}>Category & Goal</th>
                  <th style={{ padding: '14px 16px' }}>Showcase Status</th>
                  <th style={{ padding: '14px 16px' }}>Moderation</th>
                  <th style={{ padding: '14px 16px' }}>Created</th>
                  <th style={{ padding: '14px 16px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 14 }}>
                        <Link to={`/projects/${p.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                          {p.title}
                        </Link>
                      </div>
                      {p.tagline && (
                        <div style={{ fontSize: 12, color: 'var(--text-secondary)', maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {p.tagline}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      {p.owner ? (
                        <div>
                          <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{p.owner.full_name}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{p.owner.email}</div>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>#{p.owner_id.slice(0, 8)}</span>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{p.category || 'General'}</div>
                      <div style={{ fontSize: 12, color: 'var(--brand-emerald)' }}>
                        ${p.funding_goal ? Number(p.funding_goal).toLocaleString() : '0'} target
                      </div>
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <Badge variant={p.status === 'published' ? 'cyan' : 'secondary'}>
                        {p.status}
                      </Badge>
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <Badge
                        variant={
                          p.moderation_status === 'approved'
                            ? 'emerald'
                            : p.moderation_status === 'rejected'
                            ? 'rose'
                            : 'amber'
                        }
                      >
                        {p.moderation_status || 'pending_review'}
                      </Badge>
                      {p.moderation_reason && (
                        <div style={{ fontSize: 11, color: 'var(--brand-rose)', marginTop: 4, maxWidth: 160 }} title={p.moderation_reason}>
                          {p.moderation_reason}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(p.created_at).toLocaleDateString()}
                    </td>

                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                        <Link to={`/projects/${p.id}`} className="btn btn-ghost btn-sm" target="_blank" rel="noopener noreferrer">
                          View
                        </Link>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => {
                            setSelectedProject(p);
                            setReviewMode('view');
                            setRejectionReason('');
                          }}
                        >
                          Moderate
                        </button>
                      </div>
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
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} projects
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
      {selectedProject && (
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
          <div className="card" style={{ maxWidth: 580, width: '100%', backgroundColor: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: 20, marginBottom: 6 }}>Review Showcase: {selectedProject.title}</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
              Category: <strong style={{ color: 'var(--text-primary)' }}>{selectedProject.category}</strong> · Goal: <strong style={{ color: 'var(--brand-emerald)' }}>${Number(selectedProject.funding_goal || 0).toLocaleString()}</strong>
            </p>

            <div
              style={{
                backgroundColor: 'rgba(7, 9, 14, 0.6)',
                padding: 16,
                borderRadius: 'var(--radius-md)',
                marginBottom: 20,
                maxHeight: 220,
                overflowY: 'auto',
                fontSize: 13,
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
              }}
            >
              {selectedProject.description || 'No description provided.'}
            </div>

            {reviewMode === 'view' ? (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <Link to={`/projects/${selectedProject.id}`} className="btn btn-ghost btn-sm" target="_blank">
                  Open Showcase Page ↗
                </Link>

                <div style={{ display: 'flex', gap: 10 }}>
                  <Button variant="secondary" size="sm" onClick={() => setSelectedProject(null)} disabled={isSubmitting}>
                    Close
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    style={{ color: 'var(--brand-rose)', borderColor: 'var(--brand-rose)' }}
                    onClick={() => setReviewMode('reject')}
                    disabled={isSubmitting}
                  >
                    Reject Showcase
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleApprove(selectedProject.id)}
                    isLoading={isSubmitting}
                  >
                    Approve Showcase
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleReject}>
                <div className="form-group">
                  <label className="form-label">Rejection Reason (Feedback for founder)</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    placeholder="Specify why this project cannot be approved (e.g. incomplete pitch, missing milestones, prohibited category)..."
                    required
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                  <Button variant="secondary" size="sm" onClick={() => setReviewMode('view')} disabled={isSubmitting}>
                    Back
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    type="submit"
                    style={{ color: 'var(--brand-rose)', borderColor: 'var(--brand-rose)' }}
                    isLoading={isSubmitting}
                  >
                    Confirm Rejection
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminProjectsPage;
