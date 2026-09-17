import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';

export function AdminAuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');

  // Expanded details row
  const [expandedLogId, setExpandedLogId] = useState(null);

  useEffect(() => {
    loadAuditLogs();
  }, [page, actionFilter, entityFilter]);

  const loadAuditLogs = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = {
        page,
        limit,
        action: actionFilter || undefined,
        entity_type: entityFilter || undefined,
      };
      const res = await adminService.getAdminAuditLogs(params);
      setLogs(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setError(err.message || 'Failed to fetch audit log trail');
    } finally {
      setIsLoading(false);
    }
  };

  const getActionBadgeVariant = (action) => {
    if (action.includes('suspend') || action.includes('reject') || action.includes('revoke')) return 'rose';
    if (action.includes('verify') || action.includes('approve') || action.includes('resolve')) return 'emerald';
    if (action.includes('dispute')) return 'indigo';
    return 'cyan';
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>Immutable Administrative Audit Trail</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Cryptographically anchored governance logs. Every administrative mutation records the verified admin ID and server timestamp.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Badge variant="emerald">Append-Only</Badge>
          <Badge variant="cyan">{total} Events Logged</Badge>
        </div>
      </div>

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
          <div style={{ flex: '0 1 240px' }}>
            <select
              className="form-select"
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Action: All Actions</option>
              <option value="verify_user">verify_user</option>
              <option value="revoke_verification">revoke_verification</option>
              <option value="suspend_user">suspend_user</option>
              <option value="unsuspend_user">unsuspend_user</option>
              <option value="approve_project">approve_project</option>
              <option value="reject_project">reject_project</option>
              <option value="resolve_report">resolve_report</option>
              <option value="dismiss_report">dismiss_report</option>
              <option value="resolve_dispute">resolve_dispute</option>
              <option value="dismiss_dispute">dismiss_dispute</option>
            </select>
          </div>

          <div style={{ flex: '0 1 200px' }}>
            <select
              className="form-select"
              value={entityFilter}
              onChange={(e) => {
                setEntityFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Entity: All Entities</option>
              <option value="user">User</option>
              <option value="project">Project</option>
              <option value="report">Report</option>
              <option value="dispute">Dispute</option>
            </select>
          </div>

          {(actionFilter || entityFilter) && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setActionFilter('');
                setEntityFilter('');
                setPage(1);
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} />
          </div>
        ) : logs.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No audit records match the current filter.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ backgroundColor: 'rgba(13, 18, 29, 0.7)', borderBottom: '1px solid var(--border-medium)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '14px 16px' }}>Timestamp (UTC)</th>
                  <th style={{ padding: '14px 16px' }}>Admin Identity</th>
                  <th style={{ padding: '14px 16px' }}>Action Executed</th>
                  <th style={{ padding: '14px 16px' }}>Target Entity</th>
                  <th style={{ padding: '14px 16px' }}>IP Origin</th>
                  <th style={{ padding: '14px 16px', textAlign: 'right' }}>Metadata</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: isExpanded ? 'rgba(99, 102, 241, 0.05)' : 'transparent' }}>
                        <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                          {new Date(log.created_at).toLocaleString()}
                        </td>

                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            {log.admin ? log.admin.full_name : 'Admin User'}
                          </div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                            {log.admin ? log.admin.email : `#${log.admin_id.slice(0, 8)}`}
                          </div>
                        </td>

                        <td style={{ padding: '14px 16px' }}>
                          <Badge variant={getActionBadgeVariant(log.action)}>
                            {log.action}
                          </Badge>
                        </td>

                        <td style={{ padding: '14px 16px', color: 'var(--brand-cyan)' }}>
                          {log.entity_type} #{log.entity_id ? log.entity_id.slice(0, 8) : 'N/A'}
                        </td>

                        <td style={{ padding: '14px 16px', color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: 12 }}>
                          {log.ip_address || '127.0.0.1'}
                        </td>

                        <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                          <button
                            className="btn btn-ghost btn-sm"
                            style={{ padding: '4px 8px', fontSize: 12 }}
                            onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                          >
                            {isExpanded ? 'Hide ▲' : 'Details ▼'}
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(7, 9, 14, 0.6)' }}>
                          <td colSpan={6} style={{ padding: '16px 20px' }}>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase' }}>
                              Audit Payload & Mutation Context
                            </div>
                            <pre
                              style={{
                                backgroundColor: 'rgba(13, 18, 29, 0.95)',
                                padding: 14,
                                borderRadius: 'var(--radius-sm)',
                                fontSize: 12,
                                color: 'var(--brand-cyan)',
                                overflowX: 'auto',
                                border: '1px solid var(--border-subtle)',
                              }}
                            >
                              {JSON.stringify({
                                log_id: log.id,
                                admin_id: log.admin_id,
                                action: log.action,
                                entity_type: log.entity_type,
                                entity_id: log.entity_id,
                                timestamp: log.created_at,
                                details: log.details || {},
                              }, null, 2)}
                            </pre>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {total > limit && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} audit records
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
    </div>
  );
}

export default AdminAuditLogsPage;
