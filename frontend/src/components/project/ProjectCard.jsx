import React from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '../common/Badge';
import { TrustScoreBadge } from '../common/TrustScoreBadge';
import { Button } from '../common/Button';
import { formatCurrency } from '../../utils/currency';

export function ProjectCard({
  project,
  isOwner = false,
  onArchive,
  onPublish,
  onSponsor,
  showActions = true,
}) {
  if (!project) return null;

  const {
    id,
    title,
    tagline,
    category,
    industry,
    stage = 'idea',
    status = 'published',
    funding_goal = 0,
    funding_received = 0,
    current_funding = 0,
    required_support = [],
    currency = 'INR',
    location,
    cover_image_url,
    logo_url,
    founder,
  } = project;

  const currentAmount = current_funding || funding_received || 0;
  const targetAmount = funding_goal || 1;
  const progressPct = Math.min(100, Math.round((currentAmount / targetAmount) * 100));

  const displayImage = logo_url || cover_image_url;

  const getStatusBadge = (st) => {
    const s = (st || '').toLowerCase();
    switch (s) {
      case 'draft':
        return <Badge variant="amber">Draft</Badge>;
      case 'seeking_sponsorship':
        return <Badge variant="cyan">Seeking Sponsorship</Badge>;
      case 'in_discussion':
        return <Badge variant="indigo">In Discussion</Badge>;
      case 'funded':
        return <Badge variant="emerald">Funded</Badge>;
      case 'completed':
        return <Badge variant="emerald">Completed</Badge>;
      case 'archived':
        return <Badge variant="slate">Archived</Badge>;
      case 'published':
      case 'active':
      default:
        return <Badge variant="cyan">Published</Badge>;
    }
  };

  const getStageBadge = (stg) => {
    const s = (stg || '').toLowerCase();
    switch (s) {
      case 'prototype':
        return <Badge variant="indigo">Prototype</Badge>;
      case 'mvp':
        return <Badge variant="cyan">MVP</Badge>;
      case 'launched':
        return <Badge variant="emerald">Launched</Badge>;
      case 'scaling':
        return <Badge variant="purple">Scaling</Badge>;
      case 'idea':
      default:
        return <Badge variant="slate">Idea</Badge>;
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
        {/* Top Header: Logo / Category & Status */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 14 }}>
          {displayImage ? (
            <img
              src={displayImage}
              alt={title}
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
                background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 22,
                flexShrink: 0,
              }}
            >
              💡
            </div>
          )}

          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 12, color: 'var(--brand-cyan)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {category || 'Innovation'}
              </span>
              {getStatusBadge(status)}
            </div>
            <Link
              to={`/projects/${id}`}
              style={{
                textDecoration: 'none',
                color: 'var(--text-primary)',
              }}
            >
              <h3
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  lineHeight: 1.3,
                  marginBottom: 2,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
                title={title}
              >
                {title}
              </h3>
            </Link>
            {industry && (
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {industry}
              </span>
            )}
          </div>
        </div>

        {/* Tagline */}
        <p
          style={{
            fontSize: 13,
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            marginBottom: 16,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            minHeight: 38,
          }}
        >
          {tagline || 'Innovative startup initiative on the Vynk trust network.'}
        </p>

        {/* Badges: Stage & Support Tags */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
          {getStageBadge(stage)}
          {(required_support || []).slice(0, 3).map((supp) => (
            <span
              key={supp}
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'var(--text-secondary)',
              }}
            >
              {supp}
            </span>
          ))}
          {(required_support || []).length > 3 && (
            <span style={{ fontSize: 11, color: 'var(--text-muted)', alignSelf: 'center' }}>
              +{required_support.length - 3} more
            </span>
          )}
          {location && (
            <span
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
              }}
            >
              📍 {location}
            </span>
          )}
        </div>

        {/* Funding Progress Bar */}
        <div
          style={{
            padding: '10px 12px',
            backgroundColor: 'rgba(7, 9, 14, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            marginBottom: 16,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, marginBottom: 6 }}>
            <span style={{ color: 'var(--text-muted)' }}>Funding Progress</span>
            <strong style={{ color: 'var(--brand-emerald)' }}>{progressPct}%</strong>
          </div>
          <div
            style={{
              width: '100%',
              height: 6,
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              borderRadius: 3,
              overflow: 'hidden',
              marginBottom: 6,
            }}
          >
            <div
              style={{
                width: `${progressPct}%`,
                height: '100%',
                background: 'linear-gradient(90deg, var(--brand-cyan) 0%, var(--brand-emerald) 100%)',
                borderRadius: 3,
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-secondary)' }}>
            <span>{formatCurrency(currentAmount, currency)} received</span>
            <span>Goal: <strong>{formatCurrency(targetAmount, currency)}</strong></span>
          </div>
        </div>
      </div>

      {/* Footer: Founder Info & Actions */}
      <div>
        {founder && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingTop: 12,
              borderTop: '1px solid var(--border-subtle)',
              marginBottom: showActions ? 14 : 0,
            }}
          >
            <Link
              to={founder.username ? `/p/${founder.username}` : '#'}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                textDecoration: 'none',
                color: 'var(--text-primary)',
              }}
            >
              {founder.avatar_url ? (
                <img
                  src={founder.avatar_url}
                  alt={founder.full_name}
                  style={{ width: 26, height: 26, borderRadius: '50%', objectFit: 'cover' }}
                />
              ) : (
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(6, 182, 212, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 12,
                    color: 'var(--brand-cyan)',
                  }}
                >
                  👤
                </div>
              )}
              <span style={{ fontSize: 13, fontWeight: 500 }}>{founder.full_name}</span>
            </Link>

            <TrustScoreBadge score={founder.trust_score || 50} size="sm" showLabel={false} />
          </div>
        )}

        {/* Action Buttons */}
        {showActions && (
          <div style={{ display: 'flex', gap: 8, marginTop: founder ? 0 : 8 }}>
            {isOwner ? (
              <>
                <Link to={`/projects/${id}`} style={{ flex: 1, textDecoration: 'none' }}>
                  <Button variant="ghost" size="sm" style={{ width: '100%' }}>
                    View
                  </Button>
                </Link>
                <Link to={`/projects/${id}/edit`} style={{ flex: 1, textDecoration: 'none' }}>
                  <Button variant="secondary" size="sm" style={{ width: '100%' }}>
                    Edit
                  </Button>
                </Link>
                {status.toLowerCase() === 'draft' && onPublish && (
                  <Button variant="primary" size="sm" onClick={() => onPublish(project)}>
                    Publish
                  </Button>
                )}
                {status.toLowerCase() !== 'archived' && onArchive && (
                  <Button variant="ghost" size="sm" onClick={() => onArchive(project)} title="Archive Project">
                    Archive
                  </Button>
                )}
              </>
            ) : onSponsor ? (
              <>
                <Link to={`/projects/${id}`} style={{ flex: 1, textDecoration: 'none' }}>
                  <Button variant="ghost" size="sm" style={{ width: '100%' }}>
                    Details
                  </Button>
                </Link>
                <Button variant="emerald" size="sm" style={{ flex: 1.4 }} onClick={() => onSponsor(project)}>
                  Propose Support
                </Button>
              </>
            ) : (
              <Link to={`/projects/${id}`} style={{ width: '100%', textDecoration: 'none' }}>
                <Button variant="secondary" size="sm" style={{ width: '100%' }}>
                  View Project Showcase →
                </Button>
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
