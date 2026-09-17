import React from 'react';
import { Button } from '../common/Button';

export function ProfileCompletionCard({ completion, onEditClick }) {
  if (!completion) return null;

  const { percentage = 0, completed_fields = [], missing_fields = [], tips = [] } = completion;
  const isComplete = percentage >= 100;

  // Determine accent color and badge based on score
  let statusColor = 'var(--brand-cyan)';
  let statusText = 'Getting Started';
  if (percentage >= 100) {
    statusColor = 'var(--brand-emerald)';
    statusText = 'All-Star Profile';
  } else if (percentage >= 70) {
    statusColor = 'var(--brand-cyan)';
    statusText = 'Strong Profile';
  } else if (percentage >= 40) {
    statusColor = 'var(--brand-amber)';
    statusText = 'Intermediate';
  }

  return (
    <div
      className="card"
      style={{
        marginBottom: 28,
        background: isComplete
          ? 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(16, 185, 129, 0.12) 100%)'
          : 'linear-gradient(135deg, rgba(18, 25, 39, 0.95) 0%, rgba(6, 182, 212, 0.09) 100%)',
        border: `1px solid ${isComplete ? 'rgba(16, 185, 129, 0.3)' : 'rgba(6, 182, 212, 0.25)'}`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative top accent glow */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 3,
          background: isComplete
            ? 'linear-gradient(90deg, var(--brand-emerald), var(--brand-cyan))'
            : 'linear-gradient(90deg, var(--brand-cyan), var(--brand-indigo))',
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', fontWeight: 600 }}>
              Profile Strength
            </span>
            <span
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: statusColor,
                backgroundColor: `${statusColor}18`,
                padding: '2px 8px',
                borderRadius: 999,
                border: `1px solid ${statusColor}40`,
              }}
            >
              {statusText}
            </span>
          </div>
          <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>
            {isComplete ? 'Your Vynk Profile is 100% Complete!' : `${percentage}% Completed`}
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Button variant={isComplete ? 'secondary' : 'primary'} size="sm" onClick={onEditClick}>
            {isComplete ? 'Update Profile' : 'Complete Profile →'}
          </Button>
        </div>
      </div>

      {/* Animated Glowing Progress Bar */}
      <div
        style={{
          width: '100%',
          height: 10,
          backgroundColor: 'rgba(255, 255, 255, 0.07)',
          borderRadius: 999,
          overflow: 'hidden',
          marginBottom: 16,
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percentage}%`,
            background: isComplete
              ? 'linear-gradient(90deg, #10B981 0%, #06B6D4 100%)'
              : 'linear-gradient(90deg, #06B6D4 0%, #3B82F6 50%, #10B981 100%)',
            borderRadius: 999,
            transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
            boxShadow: `0 0 12px ${statusColor}60`,
          }}
        />
      </div>

      {/* Completion Details & Tips */}
      {!isComplete && tips && tips.length > 0 && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 500 }}>
            Suggested actions to reach 100%:
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {tips.map((tip, idx) => (
              <div
                key={idx}
                onClick={onEditClick}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 13,
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(255, 255, 255, 0.03)',
                  transition: 'background 0.2s ease',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(6, 182, 212, 0.1)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)')}
              >
                <span style={{ color: 'var(--brand-cyan)', fontSize: 14 }}>⚡</span>
                <span>{tip}</span>
                <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--brand-cyan)' }}>Add →</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {isComplete && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--brand-emerald)', marginTop: 8 }}>
          <span>✓</span>
          <span>Your profile is fully optimized for maximum discoverability and sponsor AI matching.</span>
        </div>
      )}
    </div>
  );
}
