import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { Button } from '../../components/common/Button';

export function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [verifiedFilter, setVerifiedFilter] = useState('');
  const [suspendedFilter, setSuspendedFilter] = useState('');

  // Modals state
  const [activeModal, setActiveModal] = useState(null); // 'verify' | 'revoke' | 'suspend' | 'unsuspend'
  const [selectedUser, setSelectedUser] = useState(null);
  const [modalInput, setModalInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadUsers();
  }, [page, roleFilter, verifiedFilter, suspendedFilter]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = {
        page,
        limit,
        search: search.trim() || undefined,
        role: roleFilter || undefined,
        is_verified: verifiedFilter === '' ? undefined : verifiedFilter === 'true',
        is_suspended: suspendedFilter === '' ? undefined : suspendedFilter === 'true',
      };

      const res = await adminService.getAdminUsers(params);
      setUsers(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load users:', err);
      setError(err.message || 'Failed to fetch user list');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadUsers();
  };

  const openActionModal = (type, user) => {
    setActiveModal(type);
    setSelectedUser(user);
    setModalInput('');
  };

  const closeActionModal = () => {
    setActiveModal(null);
    setSelectedUser(null);
    setModalInput('');
    setIsSubmitting(false);
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUser) return;

    try {
      setIsSubmitting(true);
      setError(null);

      if (activeModal === 'verify') {
        await adminService.verifyUser(selectedUser.id, { notes: modalInput.trim() || undefined });
        setSuccessMessage(`User "${selectedUser.full_name}" successfully verified. Trust Score recalculated.`);
      } else if (activeModal === 'revoke') {
        if (!modalInput.trim()) {
          setError('Reason for revoking verification is required');
          setIsSubmitting(false);
          return;
        }
        await adminService.revokeUserVerification(selectedUser.id, { reason: modalInput.trim() });
        setSuccessMessage(`Verification revoked for "${selectedUser.full_name}". Trust Score recalculated.`);
      } else if (activeModal === 'suspend') {
        if (!modalInput.trim()) {
          setError('Suspension reason is required');
          setIsSubmitting(false);
          return;
        }
        await adminService.suspendUser(selectedUser.id, { reason: modalInput.trim() });
        setSuccessMessage(`User "${selectedUser.full_name}" has been suspended. Platform access disabled.`);
      } else if (activeModal === 'unsuspend') {
        await adminService.unsuspendUser(selectedUser.id);
        setSuccessMessage(`User "${selectedUser.full_name}" unsuspended. Platform access restored.`);
      }

      closeActionModal();
      loadUsers();
    } catch (err) {
      console.error('Action failed:', err);
      setError(err.message || 'Action execution failed');
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>User Management & Identity Verification</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Inspect user profiles, verify accredited credentials, enforce suspensions, and monitor Trust Scores.
          </p>
        </div>
        <Badge variant="cyan">{total} Users Registered</Badge>
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

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: 24, padding: 20 }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: 14, alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by name, email, company, headline..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ flex: '0 1 150px' }}>
            <select className="form-select" value={roleFilter} onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}>
              <option value="">All Roles</option>
              <option value="entrepreneur">Entrepreneurs</option>
              <option value="sponsor">Sponsors</option>
              <option value="admin">Admins</option>
            </select>
          </div>

          <div style={{ flex: '0 1 160px' }}>
            <select className="form-select" value={verifiedFilter} onChange={(e) => { setVerifiedFilter(e.target.value); setPage(1); }}>
              <option value="">Verification: All</option>
              <option value="true">Verified Only</option>
              <option value="false">Unverified Only</option>
            </select>
          </div>

          <div style={{ flex: '0 1 160px' }}>
            <select className="form-select" value={suspendedFilter} onChange={(e) => { setSuspendedFilter(e.target.value); setPage(1); }}>
              <option value="">Status: All</option>
              <option value="false">Active Accounts</option>
              <option value="true">Suspended Only</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-sm">
            Search
          </button>
          {(search || roleFilter || verifiedFilter || suspendedFilter) && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setSearch('');
                setRoleFilter('');
                setVerifiedFilter('');
                setSuspendedFilter('');
                setPage(1);
              }}
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Users Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} />
          </div>
        ) : users.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No users matched your search criteria.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ backgroundColor: 'rgba(13, 18, 29, 0.7)', borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '14px 16px' }}>User Details</th>
                  <th style={{ padding: '14px 16px' }}>Role</th>
                  <th style={{ padding: '14px 16px' }}>Verification</th>
                  <th style={{ padding: '14px 16px' }}>Status</th>
                  <th style={{ padding: '14px 16px' }}>Trust Score</th>
                  <th style={{ padding: '14px 16px' }}>Registered</th>
                  <th style={{ padding: '14px 16px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: '50%',
                            backgroundColor: 'rgba(99, 102, 241, 0.2)',
                            color: 'var(--brand-indigo)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: 14,
                            border: '1px solid rgba(99, 102, 241, 0.3)',
                          }}
                        >
                          {u.full_name ? u.full_name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            <Link to={`/profile/${u.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                              {u.full_name}
                            </Link>
                          </div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{u.email}</div>
                          {u.company_name && (
                            <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>🏢 {u.company_name}</div>
                          )}
                        </div>
                      </div>
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <Badge variant={u.role === 'sponsor' ? 'emerald' : u.role === 'admin' ? 'indigo' : 'cyan'}>
                        {u.role}
                      </Badge>
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      {u.is_verified ? (
                        <span style={{ color: 'var(--brand-emerald)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          <span>✓</span> Verified
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>Unverified</span>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      {u.is_suspended ? (
                        <div>
                          <Badge variant="rose">Suspended</Badge>
                          {u.suspension_reason && (
                            <div style={{ fontSize: 11, color: 'var(--brand-rose)', marginTop: 4, maxWidth: 160 }} title={u.suspension_reason}>
                              {u.suspension_reason}
                            </div>
                          )}
                        </div>
                      ) : (
                        <Badge variant="emerald">Active</Badge>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <TrustScoreBadge score={u.trust_score?.score ?? 50} size="sm" showLabel={false} />
                    </td>

                    <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>

                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                        {!u.is_verified ? (
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ color: 'var(--brand-emerald)' }}
                            onClick={() => openActionModal('verify', u)}
                          >
                            Verify
                          </button>
                        ) : (
                          <button
                            className="btn btn-ghost btn-sm"
                            style={{ color: 'var(--text-muted)' }}
                            onClick={() => openActionModal('revoke', u)}
                          >
                            Revoke
                          </button>
                        )}

                        {!u.is_suspended ? (
                          <button
                            className="btn btn-ghost btn-sm"
                            style={{ color: 'var(--brand-rose)' }}
                            onClick={() => openActionModal('suspend', u)}
                          >
                            Suspend
                          </button>
                        ) : (
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ color: 'var(--brand-cyan)' }}
                            onClick={() => openActionModal('unsuspend', u)}
                          >
                            Unsuspend
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {total > limit && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} accounts
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page * limit >= total}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Action Modal */}
      {activeModal && selectedUser && (
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
          <div className="card" style={{ maxWidth: 480, width: '100%', backgroundColor: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>
              {activeModal === 'verify' && `Verify User: ${selectedUser.full_name}`}
              {activeModal === 'revoke' && `Revoke Verification: ${selectedUser.full_name}`}
              {activeModal === 'suspend' && `Suspend Account: ${selectedUser.full_name}`}
              {activeModal === 'unsuspend' && `Unsuspend Account: ${selectedUser.full_name}`}
            </h3>

            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 20 }}>
              {activeModal === 'verify' && 'Confirming this user sets their verified flag and triggers algorithmic Trust Score recalculation (+15pts in Verification pillar).'}
              {activeModal === 'revoke' && 'Revoking verification returns the user to unverified status and deducts verification pillar Trust Score points.'}
              {activeModal === 'suspend' && 'Suspended users are blocked from authenticated platform operations. An audit log will record your admin identity.'}
              {activeModal === 'unsuspend' && 'Restore normal platform access and authenticated actions for this user.'}
            </p>

            <form onSubmit={handleModalSubmit}>
              {activeModal === 'verify' && (
                <div className="form-group">
                  <label className="form-label">Verification Notes (Optional)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Identity documents reviewed and accredited sponsor confirmed."
                    value={modalInput}
                    onChange={(e) => setModalInput(e.target.value)}
                  />
                </div>
              )}

              {activeModal === 'revoke' && (
                <div className="form-group">
                  <label className="form-label">Revocation Reason (Required)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Failure to maintain compliance documents."
                    required
                    value={modalInput}
                    onChange={(e) => setModalInput(e.target.value)}
                  />
                </div>
              )}

              {activeModal === 'suspend' && (
                <div className="form-group">
                  <label className="form-label">Suspension Reason (Required)</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    placeholder="Provide detailed violation rationale for the audit record..."
                    required
                    value={modalInput}
                    onChange={(e) => setModalInput(e.target.value)}
                  />
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                <Button variant="secondary" size="sm" onClick={closeActionModal} disabled={isSubmitting}>
                  Cancel
                </Button>
                <Button
                  variant={activeModal === 'suspend' || activeModal === 'revoke' ? 'secondary' : 'primary'}
                  size="sm"
                  type="submit"
                  isLoading={isSubmitting}
                  style={activeModal === 'suspend' || activeModal === 'revoke' ? { color: 'var(--brand-rose)', borderColor: 'var(--brand-rose)' } : {}}
                >
                  {activeModal === 'verify' && 'Confirm Verification'}
                  {activeModal === 'revoke' && 'Revoke Verification'}
                  {activeModal === 'suspend' && 'Suspend User'}
                  {activeModal === 'unsuspend' && 'Unsuspend User'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsersPage;
