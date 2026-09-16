import React from 'react';

export function Input({
  label,
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  required = false,
  helperText,
  className = '',
  ...props
}) {
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={id} className="form-label">
          {label} {required && <span style={{ color: 'var(--brand-cyan)' }}>*</span>}
        </label>
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`form-input ${error ? 'input-has-error' : ''} ${className}`}
        style={error ? { borderColor: 'var(--brand-rose)' } : {}}
        {...props}
      />
      {helperText && !error && (
        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
          {helperText}
        </span>
      )}
      {error && <span className="form-error">{error}</span>}
    </div>
  );
}
