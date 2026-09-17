import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../services/api';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export function TrustScoreBreakdownModal({ isOpen, onClose, userId = null, isPublic = false }) {
  const [trustData, setTrustData] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecalculating, setIsRecalculating] = useState(false);
  const [activeTab, setActiveTab] = useState('breakdown'); // 'breakdown' | 'history'
  const [recalcMessage, setRecalcMessage] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    const fetchData = async () => {
      setIsLoading(true);
      setRecalcMessage('');
      try {
        if (userId && isPublic) {
          // Public profile view
          const publicRes = await apiRequest(`/trust/users/${userId}`);
          setTrustData(publicRes);
          setHistory([]);
        } else {
          // Own profile view
          const [scoreRes, historyRes] = await Promise.all([
            apiRequest('/trust/me'),
            apiRequest('/trust/history'),
          ]);
          setTrustData(scoreRes);
          setHistory(historyRes?.events || []);
        }
      } catch (err) {
        console.error('Failed to load trust score data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [isOpen, userId, isPublic]);

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    setRecalcMessage('');
    try {
      const res = await apiRequest('/trust/recalculate', { method: 'POST' });
      setTrustData(res);
      setRecalcMessage('Trust Score verified & recalculated against all factual records!');
      // Refresh history
      const historyRes = await apiRequest('/trust/history').catch(() => null);
      if (historyRes) setHistory(historyRes.events || []);
    } catch (err) {
      console.error('Failed to recalculate trust score:', err);
      setRecalcMessage('Recalculation failed. Please try again.');
    } finally {
      setIsRecalculating(false);
    }
  };

  if (!isOpen) return null;

  const score = trustData?.score ?? 50;
  let scoreColor = '#10B981';
  let tierLabel = 'High Trust';
  if (score < 50) {
    scoreColor = '#F59E0B';
    tierLabel = 'Building Trust';
  } else if (score < 75) {
    scoreColor = '#06B6D4';
    tierLabel = 'Good Standing';
  }

  const categories = [
    {
      key: 'verification',
      name: 'Platform Verification',
      current: trustData?.verification_score ?? 0,
      max: 25,
      description: 'Email verification (+10) and complete profile setup (+15).',
      color: '#06B6D4',
    },
    {
      key: 'commitment',
      name: 'Commitment Reliability',
      current: trustData?.commitment_score ?? 0,
      max: 35,
      description: 'Fulfilled sponsorship agreements (+5 each). Unilateral cancellations penalize (-10).',
      color: '#10B981',
    },
    {
      key: 'milestones',
      name: 'Milestone Execution',
      current: trustData?.milestone_score ?? 0,
      max: 20,
      description: 'Verified milestone progress with documented deliverables (+2 each, max 2 per commitment).',
      color: '#8B5CF6',
    },
    {
      key: 'activity',
      name: 'Platform Responsiveness',
      current: trustData?.activity_score ?? 0,
      max: 20,
      description: 'Timely responses to sponsorship inquiries within 48 hours (+2 each).',
      color: '#F59E0B',
    },
  ];

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(5, 7, 12, 0.85)',
        backdropFilter: 'blur(8px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#0d131f',
          border: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.1))',
          borderRadius: 16,
          width: '100%',
          maxWidth: 640,
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(6, 182, 212, 0.1)',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(6, 182, 212, 0.05) 100%)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                backgroundColor: 'rgba(6, 182, 212, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: 'var(--text-primary, #fff)' }}>
                Trust Score & Reputation
              </h3>
              <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted, #94a3b8)' }}>
                Auditable, deterministic platform credibility
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted, #94a3b8)',
              fontSize: 22,
              cursor: 'pointer',
              lineHeight: 1,
              padding: '4px 8px',
            }}
          >
            &times;
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted, #94a3b8)' }}>
              Loading reputation records...
            </div>
          ) : (
            <>
              {/* Score Hero Section */}
              <div
                style={{
                  padding: 20,
                  borderRadius: 12,
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 16,
                  marginBottom: 20,
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{ fontSize: 36, fontWeight: 700, color: scoreColor }}>
                      {score}
                    </span>
                    <span style={{ fontSize: 16, color: 'var(--text-muted, #94a3b8)', fontWeight: 500 }}>
                      / 100
                    </span>
                    <Badge variant={score >= 75 ? 'emerald' : score >= 50 ? 'cyan' : 'amber'}>
                      {tierLabel}
                    </Badge>
                  </div>
                  <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary, #cbd5e1)' }}>
                    Fulfilled Commitments: <strong style={{ color: '#fff' }}>{trustData?.completed_commitments_count || 0}</strong>
                    {trustData?.completed_milestones_count !== undefined && (
                      <> · Verified Milestones: <strong style={{ color: '#fff' }}>{trustData.completed_milestones_count}</strong></>
                    )}
                  </p>
                </div>

                {!isPublic && (
                  <div>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={handleRecalculate}
                      disabled={isRecalculating}
                    >
                      {isRecalculating ? 'Verifying...' : '⚡ Recalculate Score'}
                    </Button>
                  </div>
                )}
              </div>

              {recalcMessage && (
                <div
                  style={{
                    padding: '8px 14px',
                    borderRadius: 8,
                    marginBottom: 16,
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    color: '#10B981',
                    fontSize: 12,
                  }}
                >
                  {recalcMessage}
                </div>
              )}

              {/* Informational Callout */}
              <div
                style={{
                  padding: 12,
                  borderRadius: 8,
                  backgroundColor: 'rgba(6, 182, 212, 0.08)',
                  border: '1px solid rgba(6, 182, 212, 0.2)',
                  marginBottom: 20,
                  fontSize: 12,
                  color: 'var(--text-secondary, #cbd5e1)',
                  lineHeight: 1.5,
                }}
              >
                <strong style={{ color: '#06B6D4' }}>Deterministic Single Source of Truth:</strong> Your Trust Score is calculated solely from auditable platform facts (verified milestones, completed commitments, response times, and email verification). It is strictly separated from AI Compatibility scores.
              </div>

              {/* Tab Navigation (for private view) */}
              {!isPublic && (
                <div style={{ display: 'flex', gap: 8, marginBottom: 16, borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 8 }}>
                  <button
                    onClick={() => setActiveTab('breakdown')}
                    style={{
                      padding: '6px 14px',
                      borderRadius: 6,
                      background: activeTab === 'breakdown' ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                      color: activeTab === 'breakdown' ? '#06B6D4' : 'var(--text-muted, #94a3b8)',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    Category Breakdown
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    style={{
                      padding: '6px 14px',
                      borderRadius: 6,
                      background: activeTab === 'history' ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                      color: activeTab === 'history' ? '#06B6D4' : 'var(--text-muted, #94a3b8)',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    Audit Event History ({history.length})
                  </button>
                </div>
              )}

              {activeTab === 'breakdown' ? (
                /* Category Breakdown */
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {categories.map((cat) => {
                    const pct = Math.min(100, Math.round((cat.current / cat.max) * 100));
                    return (
                      <div
                        key={cat.key}
                        style={{
                          padding: 14,
                          borderRadius: 8,
                          backgroundColor: 'rgba(255, 255, 255, 0.02)',
                          border: '1px solid rgba(255, 255, 255, 0.05)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary, #fff)' }}>
                            {cat.name}
                          </span>
                          <span style={{ fontSize: 13, fontWeight: 600, color: cat.color }}>
                            {cat.current} <span style={{ color: 'var(--text-muted, #94a3b8)', fontWeight: 400 }}>/ {cat.max} pts</span>
                          </span>
                        </div>

                        {/* Progress bar */}
                        <div
                          style={{
                            width: '100%',
                            height: 6,
                            backgroundColor: 'rgba(255, 255, 255, 0.08)',
                            borderRadius: 3,
                            overflow: 'hidden',
                            marginBottom: 8,
                          }}
                        >
                          <div
                            style={{
                              width: `${pct}%`,
                              height: '100%',
                              backgroundColor: cat.color,
                              borderRadius: 3,
                              transition: 'width 0.3s ease',
                            }}
                          />
                        </div>

                        <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted, #94a3b8)' }}>
                          {cat.description}
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* Audit Event History (Private only) */
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {history.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted, #94a3b8)', fontSize: 13 }}>
                      No score modification events recorded yet.
                    </div>
                  ) : (
                    history.map((ev) => {
                      const isPositive = ev.points_change > 0;
                      const changeColor = isPositive ? '#10B981' : ev.points_change < 0 ? '#EF4444' : '#94A3B8';
                      const changeSign = isPositive ? `+${ev.points_change}` : `${ev.points_change}`;

                      return (
                        <div
                          key={ev.id}
                          style={{
                            padding: '10px 14px',
                            borderRadius: 8,
                            backgroundColor: 'rgba(255, 255, 255, 0.02)',
                            border: '1px solid rgba(255, 255, 255, 0.05)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            gap: 12,
                          }}
                        >
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                              <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary, #fff)' }}>
                                {ev.event_type.replace(/_/g, ' ')}
                              </span>
                              {ev.score_before !== undefined && ev.score_after !== undefined && (
                                <span style={{ fontSize: 11, color: 'var(--text-muted, #94a3b8)' }}>
                                  ({ev.score_before} → {ev.score_after})
                                </span>
                              )}
                            </div>
                            {ev.reason && (
                              <p style={{ margin: 0, fontSize: 12, color: 'var(--text-secondary, #cbd5e1)' }}>
                                {ev.reason}
                              </p>
                            )}
                            <span style={{ fontSize: 10, color: 'var(--text-muted, #64748b)' }}>
                              {new Date(ev.created_at).toLocaleString()}
                            </span>
                          </div>

                          <div
                            style={{
                              fontSize: 14,
                              fontWeight: 700,
                              color: changeColor,
                              padding: '4px 8px',
                              borderRadius: 6,
                              backgroundColor: isPositive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            }}
                          >
                            {changeSign}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '14px 24px',
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            justifyContent: 'flex-end',
            backgroundColor: 'rgba(15, 23, 42, 0.4)',
          }}
        >
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
