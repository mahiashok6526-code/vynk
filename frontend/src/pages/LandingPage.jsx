import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { TrustScoreBadge } from '../components/common/TrustScoreBadge';
import { Badge } from '../components/common/Badge';
import { VynkLogo } from '../components/common/VynkLogo';

export function LandingPage() {
  const [activeTab, setActiveTab] = useState('entrepreneur');

  return (
    <div>
      {/* Hero Section */}
      <section className="section" style={{ paddingTop: '60px', paddingBottom: '90px', position: 'relative' }}>
        <div className="container" style={{ textAlign: 'center', maxWidth: 960 }}>
          {/* Official Vynk Logo */}
          <div style={{ marginBottom: 24 }}>
            <VynkLogo variant="full" size={64} />
          </div>

          {/* Eyebrow Pill */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 16px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              marginBottom: 24,
            }}
          >
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--brand-cyan)' }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--brand-cyan)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Vynk — Ideas Meet Opportunities
            </span>
          </div>

          <h1 style={{ marginBottom: 24, fontWeight: 800 }}>
            Where Groundbreaking Ideas Meet <br />
            <span className="gradient-text">Serious Sponsorship.</span>
          </h1>

          <p style={{ fontSize: 'clamp(1.05rem, 2vw, 1.25rem)', color: 'var(--text-secondary)', marginBottom: 36, lineHeight: 1.6, maxWidth: 740, margin: '0 auto 36px' }}>
            Vynk replaces arbitrary networking with structured sponsorship commitments,
            explainable AI matching, and transparent, verifiable platform trust scores.
          </p>

          {/* Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 50 }}>
            <Link to="/register" style={{ textDecoration: 'none' }}>
              <Button variant="primary" size="lg">
                Join as Founder or Sponsor
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </Button>
            </Link>
            <a href="#how-it-works" style={{ textDecoration: 'none' }}>
              <Button variant="secondary" size="lg">
                Explore the Lifecycle
              </Button>
            </a>
          </div>

          {/* Structured Lifecycle Flow Graphic */}
          <div
            className="card"
            style={{
              padding: '20px 24px',
              backgroundColor: 'rgba(13, 18, 29, 0.75)',
              border: '1px solid var(--border-medium)',
              boxShadow: 'var(--shadow-md)',
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
              The Vynk Verified Workflow
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 12,
              }}
            >
              {[
                { label: '1. Discover', color: '#38BDF8' },
                { label: '2. AI Match', color: '#818CF8' },
                { label: '3. Connect', color: '#06B6D4' },
                { label: '4. Commit', color: '#F59E0B' },
                { label: '5. Track', color: '#EC4899' },
                { label: '6. Complete', color: '#10B981' },
                { label: '7. Build Trust', color: '#34D399' },
              ].map((step, idx, arr) => (
                <React.Fragment key={step.label}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: step.color }} />
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{step.label}</span>
                  </div>
                  {idx < arr.length - 1 && (
                    <span style={{ color: 'var(--border-medium)', fontSize: 14 }}>→</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 3 Core Differentiators Section */}
      <section id="how-it-works" className="section" style={{ backgroundColor: 'rgba(13, 18, 29, 0.5)', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: 700, margin: '0 auto 60px' }}>
            <Badge variant="cyan" style={{ marginBottom: 12 }}>Three Core Differentiators</Badge>
            <h2>Engineered for High-Stakes Collaboration</h2>
            <p style={{ marginTop: 12 }}>
              Why Vynk is fundamentally different from noisy social networks and legacy angel directories.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 28 }}>
            {/* Feature 1: AI Matching */}
            <div className="card card-hover">
              <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(99, 102, 241, 0.15)', border: '1px solid rgba(99, 102, 241, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818CF8', marginBottom: 20 }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                </svg>
              </div>
              <h3 style={{ fontSize: 20, marginBottom: 12 }}>1. Explainable AI Matching</h3>
              <p style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 20 }}>
                Multi-factor compatibility recommendations matching founders and sponsors across industry, technology, maturity stage, funding goal, and sponsorship modalities.
              </p>
              <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', border: '1px solid var(--border-subtle)', fontSize: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>CleanTech Fit Rating:</span>
                  <strong style={{ color: '#818CF8' }}>92% Match</strong>
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  ✓ Industry Alignment (+35%) · Budget Suitability (+25%) · Stage Sync (+20%)
                </div>
              </div>
            </div>

            {/* Feature 2: Structured Commitment Tracking */}
            <div className="card card-hover">
              <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(6, 182, 212, 0.15)', border: '1px solid rgba(6, 182, 212, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--brand-cyan)', marginBottom: 20 }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                  <path d="m9 15 2 2 4-4" />
                </svg>
              </div>
              <h3 style={{ fontSize: 20, marginBottom: 12 }}>2. Commitment Tracking</h3>
              <p style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 20 }}>
                Turn casual conversations into binding, structured milestones. Track status across 7 distinct phases from initial interest to disbursement and completion.
              </p>
              <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', border: '1px solid var(--border-subtle)', fontSize: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Lifecycle Pipeline:</span>
                  <Badge variant="emerald">Confirmed Stage</Badge>
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Audit log records status transitions, document references, and follow-up deadlines.
                </div>
              </div>
            </div>

            {/* Feature 3: Verifiable Trust Score */}
            <div className="card card-hover">
              <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--brand-emerald)', marginBottom: 20 }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <h3 style={{ fontSize: 20, marginBottom: 12 }}>3. Verifiable Trust Score</h3>
              <p style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 20 }}>
                Never rely on unvetted star reviews. Trust scores (0–100) are dynamically calculated from verified identity, completed commitments, response times, and project updates.
              </p>
              <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', border: '1px solid var(--border-subtle)', fontSize: 13 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Transparent Score:</span>
                  <TrustScoreBadge score={86} size="sm" />
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  25/25 Verification · 31/35 Commitments · 15/20 Response · 15/20 Activity
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Role Personas Interactive Switcher */}
      <section className="section">
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <h2 style={{ marginBottom: 12 }}>Tailored Experiences For Both Sides</h2>
            <div style={{ display: 'inline-flex', padding: 4, borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(18, 25, 39, 0.8)', border: '1px solid var(--border-subtle)', marginTop: 12 }}>
              <button
                onClick={() => setActiveTab('entrepreneur')}
                style={{
                  padding: '8px 20px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: activeTab === 'entrepreneur' ? 'var(--brand-cyan)' : 'transparent',
                  color: activeTab === 'entrepreneur' ? '#04121A' : 'var(--text-secondary)',
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                For Entrepreneurs
              </button>
              <button
                onClick={() => setActiveTab('sponsor')}
                style={{
                  padding: '8px 20px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: activeTab === 'sponsor' ? 'var(--brand-emerald)' : 'transparent',
                  color: activeTab === 'sponsor' ? '#031C13' : 'var(--text-secondary)',
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                For Sponsors & Funds
              </button>
            </div>
          </div>

          <div
            className="card"
            style={{
              padding: 40,
              maxWidth: 880,
              margin: '0 auto',
              borderColor: activeTab === 'entrepreneur' ? 'rgba(6, 182, 212, 0.3)' : 'rgba(16, 185, 129, 0.3)',
            }}
          >
            {activeTab === 'entrepreneur' ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 30, alignItems: 'center' }}>
                <div>
                  <Badge variant="cyan" style={{ marginBottom: 12 }}>Empowering Creators</Badge>
                  <h3 style={{ fontSize: 24, marginBottom: 16 }}>Showcase Ideas. Attract Serious Backing.</h3>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12, fontSize: 14, color: 'var(--text-secondary)' }}>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-cyan)' }}>✓</span>
                      Structured project profiles with itemized resource needs
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-cyan)' }}>✓</span>
                      AI match recommendations to relevant angels and corporate sponsors
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-cyan)' }}>✓</span>
                      Track active sponsorship commitments and payment tranches
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-cyan)' }}>✓</span>
                      Build a public Trust Score that unlocks larger future sponsorships
                    </li>
                  </ul>
                  <div style={{ marginTop: 24 }}>
                    <Link to="/register">
                      <Button variant="primary">Create Entrepreneur Account</Button>
                    </Link>
                  </div>
                </div>
                <div style={{ backgroundColor: 'rgba(7, 9, 14, 0.8)', borderRadius: 'var(--radius-md)', padding: 24, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8 }}>ENTREPRENEUR PREVIEW</div>
                  <h4 style={{ fontSize: 16, marginBottom: 4 }}>EcoLogix Clean Fleet</h4>
                  <p style={{ fontSize: 13, marginBottom: 16, color: 'var(--text-muted)' }}>Seeking $50,000 grant + Cloud Credits</p>
                  <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                    <Badge variant="cyan">CleanTech</Badge>
                    <Badge variant="indigo">MVP Stage</Badge>
                  </div>
                  <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Trust Score</span>
                    <TrustScoreBadge score={84} size="sm" />
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 30, alignItems: 'center' }}>
                <div>
                  <Badge variant="emerald" style={{ marginBottom: 12 }}>Strategic Backing</Badge>
                  <h3 style={{ fontSize: 24, marginBottom: 16 }}>Discover Quality Ideas. Track Real Impact.</h3>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12, fontSize: 14, color: 'var(--text-secondary)' }}>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-emerald)' }}>✓</span>
                      Curated project discoveries matching specific investment theses
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-emerald)' }}>✓</span>
                      Transparent sponsor commitment tracking with follow-up alerts
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-emerald)' }}>✓</span>
                      Verifiable entrepreneur credentials and milestone updates
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ color: 'var(--brand-emerald)' }}>✓</span>
                      Comprehensive sponsor portfolio overview and reporting
                    </li>
                  </ul>
                  <div style={{ marginTop: 24 }}>
                    <Link to="/register">
                      <Button variant="emerald">Create Sponsor Account</Button>
                    </Link>
                  </div>
                </div>
                <div style={{ backgroundColor: 'rgba(7, 9, 14, 0.8)', borderRadius: 'var(--radius-md)', padding: 24, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8 }}>SPONSOR PREVIEW</div>
                  <h4 style={{ fontSize: 16, marginBottom: 4 }}>Frontier Venture Partners</h4>
                  <p style={{ fontSize: 13, marginBottom: 16, color: 'var(--text-muted)' }}>Focus: AI & CleanTech · $10k - $250k</p>
                  <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                    <Badge variant="emerald">Venture Fund</Badge>
                    <Badge variant="cyan">3 Active Commitments</Badge>
                  </div>
                  <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Sponsor Reliability</span>
                    <TrustScoreBadge score={94} size="sm" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="section" style={{ paddingTop: 20 }}>
        <div className="container">
          <div
            className="card"
            style={{
              padding: '60px 40px',
              textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(6, 182, 212, 0.12) 100%)',
              border: '1px solid var(--border-glow)',
            }}
          >
            <h2 style={{ marginBottom: 16 }}>Ready to Connect Ideas with Real Opportunities?</h2>
            <p style={{ maxWidth: 580, margin: '0 auto 30px', color: 'var(--text-secondary)' }}>
              Join Vynk today as an entrepreneur showcasing groundbreaking projects or as a sponsor seeking verifiable innovation.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
              <Link to="/register">
                <Button variant="primary" size="lg">
                  Get Started on Vynk
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="secondary" size="lg">
                  Sign In to Your Account
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
