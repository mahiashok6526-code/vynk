import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { notificationService } from '../../services/notificationService';
import { Badge } from '../../components/common/Badge';

export function NotificationsPage() {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('all'); // all, unread, sponsorship_request, commitment, milestone, new_message, trust_score_updated, preferences
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isMarkingAll, setIsMarkingAll] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState(null);

  // Notification Preferences state
  const [preferences, setPreferences] = useState({
    in_app_messages: true,
    in_app_sponsorship_requests: true,
    in_app_commitments: true,
    in_app_milestones: true,
    in_app_follow_ups: true,
    in_app_trust_score: true,
    email_notifications: false,
  });
  const [isSavingPrefs, setIsSavingPrefs] = useState(false);

  // 1. Load Notifications
  const loadNotifications = async () => {
    setIsLoading(true);
    try {
      const isUnreadOnly = activeTab === 'unread';
      const typeFilter =
        ['all', 'unread', 'preferences'].includes(activeTab) ? null : activeTab;

      const data = await notificationService.getNotifications(50, 0, isUnreadOnly, typeFilter);
      setNotifications(data.items || []);
      setTotalCount(data.total || 0);
      setUnreadCount(data.unread_count || 0);
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to load notifications.' });
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Load Preferences
  const loadPreferences = async () => {
    try {
      const prefs = await notificationService.getNotificationPreferences();
      if (prefs) {
        setPreferences(prefs);
      }
    } catch (err) {
      // Silently catch
    }
  };

  useEffect(() => {
    if (activeTab === 'preferences') {
      loadPreferences();
    } else {
      loadNotifications();
    }
  }, [activeTab]);

  // 3. Mark Single as Read
  const handleMarkAsRead = async (notifId, e) => {
    if (e) e.stopPropagation();
    try {
      await notificationService.markNotificationRead(notifId);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notifId ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      window.dispatchEvent(new CustomEvent('vynk:refresh-unread'));
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to update notification status.' });
    }
  };

  // 4. Mark All as Read
  const handleMarkAllRead = async () => {
    if (unreadCount === 0 || isMarkingAll) return;
    setIsMarkingAll(true);
    try {
      await notificationService.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
      window.dispatchEvent(new CustomEvent('vynk:refresh-unread'));
      setFeedbackMsg({ type: 'success', text: 'All notifications marked as read.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to mark all as read.' });
    } finally {
      setIsMarkingAll(false);
    }
  };

  // 5. Update Preferences
  const handleTogglePreference = async (key) => {
    const updated = { ...preferences, [key]: !preferences[key] };
    setPreferences(updated);
    setIsSavingPrefs(true);
    try {
      await notificationService.updateNotificationPreferences({ [key]: updated[key] });
      setFeedbackMsg({ type: 'success', text: 'Notification preferences updated.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to save preference.' });
      setPreferences(preferences); // rollback
    } finally {
      setIsSavingPrefs(false);
    }
  };

  // 6. Navigate to target link
  const handleNotificationClick = (notif) => {
    if (!notif.is_read) {
      handleMarkAsRead(notif.id);
    }
    if (notif.link) {
      navigate(notif.link);
    }
  };

  const getTypeMeta = (type) => {
    switch (type) {
      case 'sponsorship_request':
        return { icon: '🤝', label: 'Proposal', variant: 'cyan', border: 'rgba(6, 182, 212, 0.4)' };
      case 'commitment':
        return { icon: '💼', label: 'Commitment', variant: 'emerald', border: 'rgba(16, 185, 129, 0.4)' };
      case 'milestone':
        return { icon: '🏆', label: 'Milestone', variant: 'purple', border: 'rgba(139, 92, 246, 0.4)' };
      case 'new_message':
      case 'message':
        return { icon: '💬', label: 'Message', variant: 'indigo', border: 'rgba(99, 102, 241, 0.4)' };
      case 'trust_score_updated':
        return { icon: '🛡️', label: 'Trust Score', variant: 'amber', border: 'rgba(245, 158, 11, 0.4)' };
      case 'follow_up':
        return { icon: '⏰', label: 'Follow-up Due', variant: 'rose', border: 'rgba(244, 63, 94, 0.4)' };
      default:
        return { icon: '🔔', label: 'System', variant: 'subtle', border: 'var(--border-subtle)' };
    }
  };

  const formatRelativeTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffSecs = Math.floor((now - date) / 1000);

    if (diffSecs < 60) return 'Just now';
    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <div className="container" style={{ padding: '32px 16px', maxWidth: 900 }}>
      {/* Page Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Notification Center</h1>
          {unreadCount > 0 && (
            <span
              style={{
                backgroundColor: 'var(--brand-amber)',
                color: '#000',
                padding: '2px 10px',
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 700,
              }}
              id="notifications-unread-count-badge"
            >
              {unreadCount} unread
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {activeTab !== 'preferences' && (
            <button
              onClick={handleMarkAllRead}
              disabled={unreadCount === 0 || isMarkingAll}
              className="btn btn-secondary btn-sm"
              style={{ opacity: unreadCount === 0 ? 0.5 : 1 }}
              id="mark-all-notifications-btn"
            >
              {isMarkingAll ? 'Marking...' : '✓ Mark All Read'}
            </button>
          )}
          <button
            onClick={() => setActiveTab(activeTab === 'preferences' ? 'all' : 'preferences')}
            className={`btn btn-sm ${activeTab === 'preferences' ? 'btn-primary' : 'btn-ghost'}`}
            id="toggle-notification-preferences-btn"
          >
            ⚙️ {activeTab === 'preferences' ? 'Back to Notifications' : 'Preferences'}
          </button>
        </div>
      </div>

      {/* Feedback Toast */}
      {feedbackMsg && (
        <div
          style={{
            marginBottom: 20,
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: feedbackMsg.type === 'error' ? 'rgba(244, 63, 94, 0.12)' : 'rgba(16, 185, 129, 0.12)',
            border: `1px solid ${feedbackMsg.type === 'error' ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
            color: feedbackMsg.type === 'error' ? '#fda4af' : '#6ee7b7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: 14,
          }}
        >
          <span>{feedbackMsg.text}</span>
          <button
            onClick={() => setFeedbackMsg(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: 16 }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs Filter (when not viewing preferences) */}
      {activeTab !== 'preferences' && (
        <div
          style={{
            display: 'flex',
            gap: 8,
            overflowX: 'auto',
            paddingBottom: 8,
            marginBottom: 24,
            borderBottom: '1px solid var(--border-subtle)',
          }}
          className="notification-tabs"
        >
          {[
            { id: 'all', label: 'All' },
            { id: 'unread', label: `Unread (${unreadCount})` },
            { id: 'sponsorship_request', label: 'Proposals' },
            { id: 'commitment', label: 'Commitments' },
            { id: 'milestone', label: 'Milestones' },
            { id: 'new_message', label: 'Messages' },
            { id: 'trust_score_updated', label: 'Trust Score' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: activeTab === tab.id ? 'var(--bg-surface-elevated)' : 'transparent',
                color: activeTab === tab.id ? 'var(--brand-cyan)' : 'var(--text-secondary)',
                border: activeTab === tab.id ? '1px solid var(--brand-cyan)' : '1px solid transparent',
                fontSize: 13,
                fontWeight: activeTab === tab.id ? 600 : 500,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
              id={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* PREFERENCES VIEW */}
      {activeTab === 'preferences' ? (
        <div
          style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: 32,
            boxShadow: 'var(--shadow-md)',
          }}
          id="notification-preferences-card"
        >
          <div style={{ marginBottom: 24 }}>
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>In-App Notification Preferences</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14, margin: 0 }}>
              Customize real-time in-app alerts triggered by backend venture events. Delivery occurs exclusively within Vynk.
            </p>
          </div>

          {/* Toggle List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              {
                key: 'in_app_messages',
                title: 'Direct Messages',
                desc: 'Receive alerts when authorized counterparties send you direct messages.',
                icon: '💬',
              },
              {
                key: 'in_app_sponsorship_requests',
                title: 'Sponsorship Proposals & Inquiries',
                desc: 'Alerts for incoming proposals, acceptances, rejections, or cancellations.',
                icon: '🤝',
              },
              {
                key: 'in_app_commitments',
                title: 'Commitments & Lifecycle Status',
                desc: 'Updates when sponsorship commitments advance (Discussion, Confirmed, Completed, etc.).',
                icon: '💼',
              },
              {
                key: 'in_app_milestones',
                title: 'Milestone & Evidence Deliverables',
                desc: 'Notified when progress updates and verifiable evidence are recorded.',
                icon: '🏆',
              },
              {
                key: 'in_app_follow_ups',
                title: 'Progress Follow-Up Reminders',
                desc: 'Alerts when scheduled commitment follow-ups and reviews become due.',
                icon: '⏰',
              },
              {
                key: 'in_app_trust_score',
                title: 'Trust Score & Reputation Changes',
                desc: 'Instant notifications when your platform Trust Score increases or recalculates.',
                icon: '🛡️',
              },
            ].map((item) => (
              <div
                key={item.key}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                  <span style={{ fontSize: 22, marginTop: 2 }}>{item.icon}</span>
                  <div>
                    <h4 style={{ fontSize: 15, fontWeight: 600, margin: '0 0 4px 0' }}>{item.title}</h4>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>{item.desc}</p>
                  </div>
                </div>

                {/* Custom Toggle Switch */}
                <label style={{ position: 'relative', display: 'inline-block', width: 46, height: 26, cursor: 'pointer', flexShrink: 0 }}>
                  <input
                    type="checkbox"
                    checked={preferences[item.key]}
                    onChange={() => handleTogglePreference(item.key)}
                    style={{ opacity: 0, width: 0, height: 0 }}
                    id={`pref-toggle-${item.key}`}
                  />
                  <span
                    style={{
                      position: 'absolute',
                      cursor: 'pointer',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: preferences[item.key] ? 'var(--brand-cyan)' : 'rgba(255, 255, 255, 0.15)',
                      borderRadius: 26,
                      transition: '0.2s',
                    }}
                  >
                    <span
                      style={{
                        position: 'absolute',
                        content: '',
                        height: 20,
                        width: 20,
                        left: preferences[item.key] ? 22 : 3,
                        bottom: 3,
                        backgroundColor: '#fff',
                        borderRadius: '50%',
                        transition: '0.2s',
                      }}
                    />
                  </span>
                </label>
              </div>
            ))}
          </div>

          {/* Extensible Future Channels Notice */}
          <div
            style={{
              marginTop: 32,
              padding: '20px 24px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px dashed var(--border-subtle)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: 0, color: 'var(--text-secondary)' }}>
                Extensible Notification Channels
              </h3>
              <span
                style={{
                  fontSize: 11,
                  padding: '2px 8px',
                  borderRadius: 4,
                  backgroundColor: 'rgba(245, 158, 11, 0.15)',
                  color: 'var(--brand-amber)',
                  fontWeight: 600,
                }}
              >
                Future Extensible Pipeline
              </span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Email digests, SMS dispatch, and mobile push notifications are supported in backend architecture for future platform versions. All notifications currently dispatch strictly in-app.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {['Email Delivery', 'SMS Direct Alert', 'Mobile Web Push'].map((channel) => (
                <div
                  key={channel}
                  style={{
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(0,0,0,0.25)',
                    border: '1px solid var(--border-subtle)',
                    opacity: 0.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{channel}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Inactive</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* NOTIFICATIONS LIST VIEW */
        <div>
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
              <div className="spinner" style={{ width: 36, height: 36 }} />
            </div>
          ) : notifications.length === 0 ? (
            <div
              style={{
                padding: '60px 20px',
                textAlign: 'center',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ fontSize: 44, marginBottom: 12 }}>🔔</div>
              <h3 style={{ fontSize: 18, color: 'var(--text-primary)', marginBottom: 6 }}>All Caught Up!</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>
                {activeTab === 'unread' ? 'No unread notifications.' : 'No notifications in this category.'}
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }} id="notifications-list">
              {notifications.map((notif) => {
                const meta = getTypeMeta(notif.type);
                return (
                  <div
                    key={notif.id}
                    onClick={() => handleNotificationClick(notif)}
                    style={{
                      padding: '18px 20px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: notif.is_read ? 'var(--bg-secondary)' : 'rgba(18, 25, 39, 0.85)',
                      border: notif.is_read ? '1px solid var(--border-subtle)' : `1px solid ${meta.border}`,
                      boxShadow: notif.is_read ? 'none' : 'var(--shadow-sm)',
                      cursor: notif.link ? 'pointer' : 'default',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 16,
                      position: 'relative',
                      transition: 'all 0.15s ease',
                    }}
                    className="notification-card"
                    id={`notification-card-${notif.id}`}
                  >
                    {/* Unread Glow Indicator */}
                    {!notif.is_read && (
                      <span
                        style={{
                          position: 'absolute',
                          top: 18,
                          left: 6,
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          backgroundColor: 'var(--brand-cyan)',
                          boxShadow: '0 0 8px var(--brand-cyan)',
                        }}
                      />
                    )}

                    {/* Icon Badge */}
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: 'var(--radius-md)',
                        backgroundColor: 'var(--bg-surface-elevated)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 18,
                        flexShrink: 0,
                      }}
                    >
                      {meta.icon}
                    </div>

                    {/* Notification Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                        <span style={{ fontSize: 15, fontWeight: notif.is_read ? 600 : 700, color: 'var(--text-primary)' }}>
                          {notif.title}
                        </span>
                        <Badge variant={meta.variant} size="sm">
                          {meta.label}
                        </Badge>
                      </div>

                      <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '0 0 8px 0', lineHeight: 1.5 }}>
                        {notif.content}
                      </p>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: 'var(--text-muted)' }}>
                        <span>{formatRelativeTime(notif.created_at)}</span>
                        {notif.link && (
                          <span style={{ color: 'var(--brand-cyan)', fontWeight: 500 }}>
                            View details →
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Action: Mark as read button */}
                    {!notif.is_read && (
                      <button
                        onClick={(e) => handleMarkAsRead(notif.id, e)}
                        className="btn btn-ghost btn-sm"
                        style={{
                          padding: '4px 8px',
                          fontSize: 11,
                          color: 'var(--text-muted)',
                          borderRadius: 4,
                          flexShrink: 0,
                        }}
                        title="Mark as read"
                      >
                        ✓ Mark read
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NotificationsPage;
