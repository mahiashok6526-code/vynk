import React from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '../common/Badge';
import { TrustScoreBadge } from '../common/TrustScoreBadge';
import { Button } from '../common/Button';
import { formatCurrency } from '../../utils/currency';

export function SponsorCard({ sponsor, onConnect }) {
  if (!sponsor) return null;

  const {
    id,
    user_id,
    full_name,
    username,
    organization_name,
    logo_url,
    avatar_url,
    headline,
    about,
    industry,
    sponsor_type = 'individual_angel',
    focus_industries = [],
    min_budget = 1000,
    max_budget = 50000,
    currency = 'INR',
    preferred_sponsorship_types = [],
    areas_supported = [],
    location,
    is_verified = false,
    trust_score = 50,
  } = sponsor;

  const displayImage = logo_url || avatar_url;

  const getSponsorTypeLabel = (st) => {
    switch ((st || '').toLowerCase()) {
      case 'venture_capital':
        return 'Venture Capital';
      case 'corporate_accelerator':
        return 'Corporate Accelerator';
      case 'grant_foundation':
        return 'Grant Foundation';
      case 'angel_network':
        return 'Angel Syndicate';
      case 'individual_angel':
      default:
        return 'Angel Investor';
    }
  };

  return (
    <div
      className="card card-hover"
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <div>
        {/* Top Header: Logo/Avatar + Sponsor Type & Verification */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 14 }}>
          {displayImage ? (
            <img
              src={displayImage}
              alt={organization_name || full_name}
              style={{
                width: 52,
                height: 52,
                borderRadius: 'var(--radius-md)',
                objectFit: 'cover',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                flexShrink: 0,
              }}
              onError={(e) => {
                e.target.onerror = null;
                e.target.style.display = 'none';
              }}
            />
          ) : (
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 'var(--radius-md)',
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 22,
                flexShrink: 0,
              }}
            >
              💼
            </div>
          )}

          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, marginBottom: 4 }}>
              <Badge variant="emerald">{getSponsorTypeLabel(sponsor_type)}</Badge>
              {is_verified && <Badge variant="cyan">Verified</Badge>}
            </div>

            <Link
              to={username ? `/p/${username}` : '#'}
              style={{
                textDecoration: 'none',
                color: 'var(--text-primary)',
              }}
            >
              <h3
                style={{
                  fontSize: 17,
                  fontWeight: 700,
                  lineHeight: 1.3,
                  marginBottom: 2,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
                title={organization_name || full_name}
              >
                {organization_name || full_name}
              </h3>
            </Link>

            {organization_name && full_name && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                Rep: {full_name}
              </div>
            )}
          </div>
        </div>

        {/* Headline / About */}
        <p
          style={{
            fontSize: 13,
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            marginBottom: 14,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            minHeight: 38,
          }}
        >
          {headline || about || 'Active strategic capital partner backing forward-looking ventures on Vynk.'}
        </p>

        {/* Budget Allocation Box in ₹ */}
        <div
          style={{
            padding: '10px 12px',
            backgroundColor: 'rgba(7, 9, 14, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            marginBottom: 14,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
            <span>Target Budget Allocation</span>
            <span style={{ color: 'var(--brand-emerald)', fontWeight: 700 }}>Active Deployer</span>
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--brand-emerald)' }}>
            {formatCurrency(min_budget, currency)} – {formatCurrency(max_budget, currency)}
          </div>
        </div>

        {/* Focus Industries & Supported Areas */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
          {industry && (
            <span
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                color: 'var(--brand-cyan)',
                fontWeight: 600,
              }}
            >
              {industry}
            </span>
          )}

          {(focus_industries || []).slice(0, 2).map((ind) => (
            <span
              key={ind}
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'var(--text-secondary)',
              }}
            >
              {ind}
            </span>
          ))}

          {(areas_supported || []).slice(0, 2).map((area) => (
            <span
              key={area}
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                color: 'var(--brand-emerald)',
              }}
            >
              {area}
            </span>
          ))}
        </div>
      </div>

      {/* Footer: Trust Score & Action Buttons */}
      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: 12,
            borderTop: '1px solid var(--border-subtle)',
            marginBottom: 12,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-muted)' }}>
            {location && (
              <>
                <span>📍</span>
                <span>{location}</span>
              </>
            )}
          </div>
          <TrustScoreBadge score={trustScore || 50} size="sm" showLabel={false} />
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          {username ? (
            <Link to={`/p/${username}`} style={{ flex: 1, textDecoration: 'none' }}>
              <Button variant="ghost" size="sm" style={{ width: '100%' }}>
                View Profile
              </Button>
            </Link>
          ) : (
            <Button variant="ghost" size="sm" style={{ flex: 1 }} disabled>
              Profile
            </Button>
          )}

          {onConnect && (
            <Button
              variant="emerald"
              size="sm"
              style={{ flex: 1.2 }}
              onClick={() => onConnect(sponsor)}
            >
              Connect →
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
