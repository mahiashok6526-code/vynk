import React from 'react';

const STAGES = [
  { key: 'interested', label: 'Interested', description: 'Initial mutual interest expressed' },
  { key: 'discussion', label: 'Discussion', description: 'Terms & scope exploration' },
  { key: 'promised', label: 'Promised', description: 'Sponsor offered term sheet' },
  { key: 'confirmed', label: 'Confirmed', description: 'Both parties aligned on terms' },
  { key: 'agreement', label: 'Agreement', description: 'Formal contract executed' },
  { key: 'funded', label: 'Funded', description: 'Capital / resources disbursed' },
  { key: 'completed', label: 'Completed', description: 'Milestones verified & fulfilled' },
];

export function CommitmentTimeline({ currentStatus = 'interested' }) {
  const isCancelled = currentStatus === 'cancelled';
  const currentIndex = STAGES.findIndex((s) => s.key === currentStatus);

  return (
    <div style={{ padding: '24px 16px', background: 'rgba(13, 18, 29, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h4 style={{ fontSize: 16, fontWeight: 700, letterSpacing: '0.02em', color: 'var(--text-primary)' }}>
          Commitment Lifecycle
        </h4>
        {isCancelled ? (
          <span style={{ padding: '4px 12px', borderRadius: 999, fontSize: 12, fontWeight: 700, backgroundColor: 'rgba(244, 63, 94, 0.15)', color: 'var(--brand-rose)', border: '1px solid rgba(244, 63, 94, 0.3)' }}>
            ● Commitment Cancelled
          </span>
        ) : (
          <span style={{ padding: '4px 12px', borderRadius: 999, fontSize: 12, fontWeight: 700, backgroundColor: 'rgba(6, 182, 212, 0.15)', color: 'var(--brand-cyan)', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
            Stage {currentIndex >= 0 ? currentIndex + 1 : 1} of 7: {currentStatus.toUpperCase()}
          </span>
        )}
      </div>

      {/* Stepper Node Track */}
      <div style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', overflowX: 'auto', paddingBottom: 10 }}>
        {/* Progress Line */}
        <div
          style={{
            position: 'absolute',
            top: 18,
            left: 20,
            right: 20,
            height: 3,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            zIndex: 0,
          }}
        >
          {!isCancelled && currentIndex > 0 && (
            <div
              style={{
                height: '100%',
                width: `${(currentIndex / (STAGES.length - 1)) * 100}%`,
                background: 'linear-gradient(90deg, var(--brand-cyan) 0%, var(--brand-emerald) 100%)',
                transition: 'width 0.4s ease',
              }}
            />
          )}
        </div>

        {STAGES.map((stage, idx) => {
          const isPassed = !isCancelled && idx < currentIndex;
          const isCurrent = !isCancelled && idx === currentIndex;
          const isPending = isCancelled || idx > currentIndex;

          let nodeBg = 'rgba(18, 25, 39, 0.9)';
          let nodeBorder = 'rgba(255, 255, 255, 0.18)';
          let nodeColor = 'var(--text-muted)';
          let nodeGlow = 'none';

          if (isPassed) {
            nodeBg = 'var(--brand-emerald)';
            nodeBorder = 'var(--brand-emerald)';
            nodeColor = '#FFFFFF';
          } else if (isCurrent) {
            nodeBg = 'var(--brand-cyan)';
            nodeBorder = 'var(--brand-cyan)';
            nodeColor = '#07090E';
            nodeGlow = '0 0 16px var(--brand-cyan-glow)';
          } else if (isCancelled) {
            nodeBg = 'rgba(18, 25, 39, 0.6)';
            nodeBorder = 'rgba(244, 63, 94, 0.2)';
          }

          return (
            <div
              key={stage.key}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                zIndex: 1,
                minWidth: 80,
                flex: 1,
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  backgroundColor: nodeBg,
                  border: `2px solid ${nodeBorder}`,
                  color: nodeColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 13,
                  fontWeight: 700,
                  boxShadow: nodeGlow,
                  marginBottom: 8,
                  transition: 'all 0.3s ease',
                }}
              >
                {isPassed ? '✓' : idx + 1}
              </div>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: isCurrent ? 700 : 500,
                  color: isCurrent ? 'var(--brand-cyan)' : isPassed ? 'var(--brand-emerald)' : 'var(--text-muted)',
                  marginBottom: 2,
                }}
              >
                {stage.label}
              </span>
              <span
                style={{
                  fontSize: 10,
                  color: 'var(--text-muted)',
                  display: 'none', // Shown on hover or larger screens
                }}
              >
                {stage.description}
              </span>
            </div>
          );
        })}
      </div>

      {isCancelled && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(244, 63, 94, 0.08)',
            border: '1px solid rgba(244, 63, 94, 0.2)',
            fontSize: 13,
            color: 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span style={{ color: 'var(--brand-rose)', fontSize: 16 }}>⚠</span>
          <span>This commitment has been marked as cancelled. No further status changes can be made.</span>
        </div>
      )}
    </div>
  );
}
