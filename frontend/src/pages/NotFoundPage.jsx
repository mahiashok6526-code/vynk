import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { VynkLogo } from '../components/common/VynkLogo';

export function NotFoundPage() {
  return (
    <div className="section" style={{ textAlign: 'center', paddingTop: 80, minHeight: '60vh' }}>
      <div className="container" style={{ maxWidth: 480, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ marginBottom: 24 }}>
          <VynkLogo variant="symbol" size={56} withLink />
        </div>
        <h1 style={{ fontSize: 72, color: 'var(--brand-cyan)', marginBottom: 16 }}>404</h1>
        <h2 style={{ fontSize: 24, marginBottom: 12 }}>Opportunity Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 30 }}>
          The page or milestone you are looking for has moved or does not exist.
        </p>
        <Link to="/">
          <Button variant="primary">Return to Vynk Home</Button>
        </Link>
      </div>
    </div>
  );
}
