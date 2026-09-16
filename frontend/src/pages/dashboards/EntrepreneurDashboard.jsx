import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../services/api';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { VynkLogo } from '../../components/common/VynkLogo';

export function EntrepreneurDashboard() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [commitments, setCommitments] = useState([]);
  const [trustScore, setTrustScore] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // New Project Form State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [tagline, setTagline] = useState('');
  const [category, setCategory] = useState('CleanTech');
  const [stage, setStage] = useState('mvp');
  const [fundingGoal, setFundingGoal] = useState(50000);
  const [description, setDescription] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [projectsRes, commitmentsRes, trustRes] = await Promise.all([
          apiRequest('/projects/my-projects').catch(() => []),
          apiRequest('/commitments/').catch(() => []),
          apiRequest('/trust/me').catch(() => null),
        ]);
        setProjects(projectsRes);
        setCommitments(commitmentsRes);
        setTrustScore(trustRes);
      } catch (err) {
        console.error('Error loading entrepreneur data:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!title.trim() || !tagline.trim() || !description.trim()) {
      setFormError('Please fill in title, tagline, and description.');
      return;
    }
    setFormError('');
    setCreateLoading(true);

    try {
      const newProj = await apiRequest('/projects/', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          tagline: tagline.trim(),
          category,
          stage,
          funding_goal: Number(fundingGoal),
          description: description.trim(),
          requirements: [
            {
              requirement_type: 'capital',
              title: 'Seed Sponsorship',
              amount: Number(fundingGoal),
            },
          ],
        }),
      });
      setProjects([newProj, ...projects]);
      setShowCreateModal(false);
      setTitle('');
      setTagline('');
      setDescription('');
    } catch (err) {
      setFormError(err.message || 'Failed to create project.');
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="section" style={{ paddingTop: 30, minHeight: '80vh' }}>
      <div className="container">
        {/* Header Profile Bar */}
        <div
          className="card"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 20,
            marginBottom: 32,
            background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.9) 0%, rgba(6, 182, 212, 0.08) 100%)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <VynkLogo variant="symbol" size={24} />
              <Badge variant="cyan">Entrepreneur Portal</Badge>
              {user?.is_verified ? (
                <Badge variant="emerald">Verified Account</Badge>
              ) : (
                <Badge variant="amber">Standard Member</Badge>
              )}
            </div>
            <h1 style={{ fontSize: 26, marginBottom: 4 }}>Welcome back, {user?.full_name}</h1>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Industry focus: <strong style={{ color: 'var(--text-primary)' }}>{user?.entrepreneur_profile?.industry || 'Startups & Innovation'}</strong> · Stage: <span style={{ textTransform: 'capitalize' }}>{user?.entrepreneur_profile?.stage || 'Idea'}</span>
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <TrustScoreBadge score={trustScore?.score ?? user?.trust_score?.score ?? 50} size="md" />
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              + New Project Showcase
            </Button>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, marginBottom: 32 }}>
          {/* Trust Score Breakdown Card */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 18 }}>Trust Score Breakdown</h3>
              <TrustScoreBadge score={trustScore?.score ?? 50} size="sm" showLabel={false} />
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Calculated dynamically from platform verification, fulfilled commitments, and responsive communication.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {(trustScore?.factors || [
                { name: 'Platform Verification', points: 0, max_points: 25 },
                { name: 'Commitment Reliability', points: 20, max_points: 35 },
                { name: 'Communication Responsiveness', points: 15, max_points: 20 },
                { name: 'Activity & Updates', points: 15, max_points: 20 },
              ]).map((f) => (
                <div key={f.name}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{f.name}</span>
                    <strong style={{ color: 'var(--text-primary)' }}>{f.points} / {f.max_points} pts</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${Math.min(100, (f.points / f.max_points) * 100)}%`,
                        height: '100%',
                        backgroundColor: 'var(--brand-cyan)',
                        borderRadius: 3,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Commitment Tracker Pipeline */}
          <div className="card">
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>Sponsorship Commitments</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Structured lifecycle of sponsor agreements backing your initiatives.
            </p>

            {commitments.length === 0 ? (
              <div style={{ padding: '30px 16px', textAlign: 'center', backgroundColor: 'rgba(7, 9, 14, 0.5)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 8 }}>No commitments recorded yet.</p>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  Once a sponsor commits to your project, structured tranches will appear here.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {commitments.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      padding: 14,
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'rgba(7, 9, 14, 0.7)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: 15, color: 'var(--text-primary)' }}>${c.amount.toLocaleString()}</strong>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Type: {c.sponsorship_type}</div>
                    </div>
                    <Badge variant={c.status === 'completed' ? 'emerald' : 'cyan'}>
                      {c.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* My Projects Showcase Section */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <h2 style={{ fontSize: 22 }}>My Projects & Startups</h2>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Your published ideas seeking sponsorship and strategic partnerships.</p>
            </div>
          </div>

          {projects.length === 0 ? (
            <div
              className="card"
              style={{
                padding: '48px 24px',
                textAlign: 'center',
                backgroundColor: 'rgba(13, 18, 29, 0.5)',
              }}
            >
              <div style={{ width: 48, height: 48, borderRadius: '50%', backgroundColor: 'rgba(6, 182, 212, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--brand-cyan)' }}>
                💡
              </div>
              <h3 style={{ fontSize: 18, marginBottom: 8 }}>No Projects Published Yet</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto 20px' }}>
                Create your first project showcase so sponsors can discover your innovation and propose structured commitments.
              </p>
              <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                Create Project Showcase
              </Button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {projects.map((p) => (
                <div key={p.id} className="card card-hover">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <Badge variant="cyan">{p.category}</Badge>
                    <Badge variant="indigo">{p.stage}</Badge>
                  </div>
                  <h3 style={{ fontSize: 18, marginBottom: 6 }}>{p.title}</h3>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>{p.tagline}</p>
                  <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(7, 9, 14, 0.6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Funding Goal:</span>
                    <strong style={{ color: 'var(--brand-cyan)' }}>${p.funding_goal.toLocaleString()}</strong>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Project Modal */}
        {showCreateModal && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(7, 9, 14, 0.85)',
              backdropFilter: 'blur(8px)',
              zIndex: 200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 20,
            }}
          >
            <div className="card" style={{ maxWidth: 540, width: '100%', maxHeight: '90vh', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h3 style={{ fontSize: 20 }}>Create Project Showcase</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              {formError && <div className="alert alert-error">{formError}</div>}

              <form onSubmit={handleCreateProject}>
                <Input
                  id="title"
                  label="Project Title"
                  placeholder="e.g. CleanAero Drone Logistics"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />

                <Input
                  id="tagline"
                  label="One-line Tagline"
                  placeholder="e.g. Autonomous zero-emission freight for regional deliveries"
                  value={tagline}
                  onChange={(e) => setTagline(e.target.value)}
                  required
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Category</label>
                    <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                      <option value="CleanTech">CleanTech</option>
                      <option value="AI & Robotics">AI & Robotics</option>
                      <option value="HealthTech">HealthTech</option>
                      <option value="FinTech">FinTech</option>
                      <option value="DeepTech">DeepTech</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Funding Goal ($)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={fundingGoal}
                      onChange={(e) => setFundingGoal(e.target.value)}
                      min={1000}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Project Description</label>
                  <textarea
                    className="form-textarea"
                    rows={4}
                    placeholder="Describe your innovation, what problem it solves, and the type of strategic sponsorship required..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                  <Button variant="ghost" onClick={() => setShowCreateModal(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary" isLoading={createLoading}>
                    Publish Project Showcase
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
