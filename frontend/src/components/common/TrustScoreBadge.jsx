import React from 'react';

export function TrustScoreBadge({ score = 50, size = 'md', showLabel = true }) {
  // Determine color hue based on score
  let scoreColor = '#10B981'; // Green (75+)
  let borderColor = 'rgba(16, 185, 129, 0.4)';
  let glowColor = 'rgba(16, 185, 129, 0.15)';

  if (score < 50) {
    scoreColor = '#F59E0B'; // Amber (< 50)
    borderColor = 'rgba(245, 158, 11, 0.4)';
    glowColor = 'rgba(245, 158, 11, 0.15)';
  } else if (score < 75) {
    scoreColor = '#06B6D4'; // Cyan (50 - 74)
    borderColor = 'rgba(6, 182, 212, 0.4)';
    glowColor = 'rgba(6, 182, 212, 0.15)';
  }

  const isSmall = size === 'sm';

  return (
    <div
      className="trust-badge"
      style={{
        borderColor,
        boxShadow: `0 0 14px ${glowColor}`,
        padding: isSmall ? '3px 10px' : '5px 14px',
      }}
      title="Verifiable Platform Trust Score based on completed commitments, responsiveness, and identity verification"
    >
      <svg
        width={isSmall ? "13" : "15"}
        height={isSmall ? "13" : "15"}
        viewBox="0 0 24 24"
        fill="none"
        stroke={scoreColor}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="m9 12 2 2 4-4" />
      </svg>
      <span
        className="trust-badge-number"
        style={{ color: scoreColor, fontSize: isSmall ? '13px' : '14px' }}
      >
        {score}
        <span style={{ fontSize: '10px', opacity: 0.65, fontWeight: 500 }}>/100</span>
      </span>
      {showLabel && (
        <span className="trust-badge-label" style={{ fontSize: isSmall ? '11px' : '12px' }}>
          Trust
        </span>
      )}
    </div>
  );
}
