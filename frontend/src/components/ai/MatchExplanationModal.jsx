import React, { useState, useEffect } from 'react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { TrustScoreBadge } from '../common/TrustScoreBadge';
import { apiRequest } from '../../services/api';
import { formatCurrency } from '../../utils/currency';

export function MatchExplanationModal({
  isOpen,
  onClose,
  targetType, // 'project' or 'sponsor'
  targetId,   // project_id when viewed by sponsor, or sponsor_id when viewed by entrepreneur
  projectId,  // optional project_id when viewed by entrepreneur
  onActionClick, // callback when user clicks primary CTA (e.g. Connect or Propose)
  actionLabel = 'Connect & Propose Support',
}) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen || !targetId) return;

    let isMounted = true;
    setIsLoading(true);
    setError('');

    const fetchExplanation = async () => {
      try {
        let endpoint = '';
        if (targetType === 'project') {
          endpoint = `/ai/matches/projects/${targetId}/explanation`;
        } else {
          endpoint = `/ai/matches/sponsors/${targetId}/explanation${projectId ? `?project_id=${projectId}` : ''}`;
        }

        const res = await apiRequest(endpoint);
        if (isMounted) {
          setData(res);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to load match explanation.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchExplanation();

    return () => {
      isMounted = false;
    };
  }, [isOpen, targetType, targetId, projectId]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(10, 15, 29, 0.82)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: 680,
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: '#0F172A',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: 16,
          padding: 0,
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
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
            background: 'linear-gradient(90deg, rgba(6, 182, 212, 0.08), rgba(16, 185, 129, 0.08))',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 20 }}>⚡</span>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                AI Compatibility Breakdown
              </h3>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Auditable multi-factor compatibility evaluation & strategic AI analysis
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: 22,
              cursor: 'pointer',
              padding: 4,
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: 24 }}>
          {isLoading ? (
            <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  border: '3px solid rgba(6, 182, 212, 0.2)',
                  borderTopColor: 'var(--brand-cyan)',
                  borderRadius: '50%',
                  margin: '0 auto 16px auto',
                  animation: 'spin 1s linear infinite',
                }}
              />
              <p style={{ fontSize: 14 }}>Evaluating compatibility factors & synthesizing rationale...</p>
            </div>
          ) : error ? (
            <div style={{ padding: 20, textAlign: 'center', color: 'var(--brand-rose)' }}>
              <p style={{ fontSize: 15, fontWeight: 600 }}>{error}</p>
              <Button variant="ghost" size="sm" onClick={onClose} style={{ marginTop: 12 }}>
                Close
              </Button>
            </div>
          ) : data ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* Score Dual-Bar: Compatibility Score vs Trust Score */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 16,
                  padding: 16,
                  borderRadius: 12,
                  backgroundColor: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                }}
              >
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Compatibility Fit
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 4 }}>
                    <span
                      style={{
                        fontSize: 32,
                        fontWeight: 800,
                        color: data.compatibility_score >= 80 ? 'var(--brand-emerald)' : 'var(--brand-cyan)',
                      }}
                    >
                      {data.compatibility_score}%
                    </span>
                    <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Match</span>
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                    Calculated from 6 objective factors
                  </div>
                </div>

                <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)', paddingLeft: 16 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Reliability Indicator
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
                    <TrustScoreBadge score={data.trust_score} size="md" />
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                    Distinct platform activity score
                  </div>
                </div>
              </div>

              {/* Factor Breakdown */}
              <div>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Factor Breakdown
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {Object.entries(data.factors || {}).map(([key, f]) => (
                    <div
                      key={key}
                      style={{
                        padding: '10px 14px',
                        backgroundColor: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: 8,
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                          {f.name}
                        </span>
                        <span style={{ fontSize: 13, fontWeight: 700, color: f.percentage >= 75 ? 'var(--brand-emerald)' : f.percentage >= 50 ? 'var(--brand-cyan)' : 'var(--brand-rose)' }}>
                          {f.score} / {f.max_score} pts ({f.percentage}%)
                        </span>
                      </div>
                      <div style={{ height: 6, backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: 999, overflow: 'hidden', marginBottom: 6 }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${f.percentage}%`,
                            backgroundColor: f.percentage >= 75 ? 'var(--brand-emerald)' : f.percentage >= 50 ? 'var(--brand-cyan)' : 'var(--brand-rose)',
                            borderRadius: 999,
                            transition: 'width 0.4s ease',
                          }}
                        />
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                        {f.detail}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reasons & Mismatches */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                {/* Why This Match */}
                <div
                  style={{
                    padding: 14,
                    backgroundColor: 'rgba(16, 185, 129, 0.04)',
                    border: '1px solid rgba(16, 185, 129, 0.18)',
                    borderRadius: 10,
                  }}
                >
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--brand-emerald)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>✓</span> Why this match?
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {(data.reasons || []).map((r, idx) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>

                {/* Considerations / Mismatches */}
                <div
                  style={{
                    padding: 14,
                    backgroundColor: 'rgba(245, 158, 11, 0.04)',
                    border: '1px solid rgba(245, 158, 11, 0.18)',
                    borderRadius: 10,
                  }}
                >
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--brand-amber)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>⚠</span> Considerations
                  </div>
                  {data.mismatches && data.mismatches.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {data.mismatches.map((m, idx) => (
                        <li key={idx}>{m}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
                      No significant friction or mismatch points identified.
                    </p>
                  )}
                </div>
              </div>

              {/* Strategic AI Explanation Box */}
              <div
                style={{
                  padding: 16,
                  borderRadius: 12,
                  background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.06), rgba(99, 102, 241, 0.06))',
                  border: '1px solid rgba(6, 182, 212, 0.25)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700, color: 'var(--brand-cyan)' }}>
                    <span>✨</span> Strategic Opportunity Analysis
                  </div>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: 999,
                      backgroundColor: data.ai_generated ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.08)',
                      color: data.ai_generated ? 'var(--brand-emerald)' : 'var(--text-muted)',
                      border: `1px solid ${data.ai_generated ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                    }}
                  >
                    {data.ai_generated ? `Google Gemini (${data.model})` : 'Deterministic Compatibility Engine'}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  "{data.explanation}"
                </p>
              </div>

              {/* Actions Footer */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 8 }}>
                <Button variant="ghost" size="md" onClick={onClose}>
                  Close
                </Button>
                {onActionClick && (
                  <Button
                    variant="primary"
                    size="md"
                    onClick={() => {
                      onClose();
                      onActionClick(data);
                    }}
                  >
                    {actionLabel}
                  </Button>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
