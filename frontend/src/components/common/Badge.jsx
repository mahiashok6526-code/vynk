import React from 'react';

export function Badge({ children, variant = 'cyan', className = '' }) {
  return (
    <span className={`badge badge-${variant} ${className}`}>
      {children}
    </span>
  );
}
