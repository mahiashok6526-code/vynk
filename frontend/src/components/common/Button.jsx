import React from 'react';

export function Button({
  children,
  variant = 'primary', // 'primary' | 'emerald' | 'secondary' | 'ghost'
  size = 'md',        // 'sm' | 'md' | 'lg'
  isLoading = false,
  disabled = false,
  className = '',
  type = 'button',
  onClick,
  ...props
}) {
  const variantClass = `btn-${variant}`;
  const sizeClass = size === 'md' ? '' : `btn-${size}`;

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`btn ${variantClass} ${sizeClass} ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <span className="spinner" style={{ width: 16, height: 16 }} />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
