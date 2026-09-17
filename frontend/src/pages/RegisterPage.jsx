import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { RoleSelector } from '../components/auth/RoleSelector';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { VynkLogo } from '../components/common/VynkLogo';

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [role, setRole] = useState('entrepreneur');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Role specific fields
  const [industry, setIndustry] = useState('AI & Machine Learning');
  const [stage, setStage] = useState('idea');
  const [organizationName, setOrganizationName] = useState('');
  const [sponsorType, setSponsorType] = useState('individual_angel');
  const [minBudget, setMinBudget] = useState(5000);
  const [maxBudget, setMaxBudget] = useState(50000);

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const errs = {};
    if (!fullName.trim()) errs.fullName = 'Full name is required.';
    if (!email.trim()) {
      errs.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errs.email = 'Enter a valid email address.';
    }
    if (!password) {
      errs.password = 'Password is required.';
    } else if (password.length < 6) {
      errs.password = 'Password must be at least 6 characters.';
    }
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    setErrors({});
    setIsLoading(true);

    try {
      const payload = {
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        password,
        role,
        ...(role === 'entrepreneur'
          ? { stage, industry }
          : {
              organization_name: organizationName.trim() || undefined,
              sponsor_type: sponsorType,
              min_budget: Number(minBudget),
              max_budget: Number(maxBudget),
            }),
      };

      const user = await register(payload);
      // Route immediately to appropriate dashboard
      navigate(user.role === 'sponsor' ? '/dashboard/sponsor' : '/dashboard/entrepreneur');
    } catch (err) {
      setApiError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <div className="container" style={{ maxWidth: 640 }}>
        <div className="card" style={{ padding: '36px 32px' }}>
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <div style={{ marginBottom: 20 }}>
              <VynkLogo variant="full" size={46} withLink />
            </div>
            <h2 style={{ fontSize: 26, marginBottom: 8 }}>Join the Vynk Network</h2>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Select your platform role and create your verified account.
            </p>
          </div>

          {apiError && (
            <div className="alert alert-error">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{apiError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Step 1: Select Role */}
            <div style={{ marginBottom: 20 }}>
              <label className="form-label" style={{ display: 'block', marginBottom: 10 }}>
                1. Select Platform Role <span style={{ color: 'var(--brand-cyan)' }}>*</span>
              </label>
              <RoleSelector selectedRole={role} onSelectRole={setRole} />
            </div>

            {/* Step 2: Account Details */}
            <div style={{ marginBottom: 20 }}>
              <label className="form-label" style={{ display: 'block', marginBottom: 12 }}>
                2. Account Information
              </label>

              <Input
                id="fullName"
                label="Full Name"
                placeholder="e.g. Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                error={errors.fullName}
                required
              />

              <Input
                id="email"
                type="email"
                label="Email Address"
                placeholder="name@organization.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                required
              />

              <Input
                id="password"
                type="password"
                label="Password"
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                helperText="Use a secure password with a combination of letters and symbols"
                required
              />
            </div>

            {/* Step 3: Role Specific Fields */}
            <div style={{ marginBottom: 28 }}>
              <label className="form-label" style={{ display: 'block', marginBottom: 12 }}>
                3. {role === 'entrepreneur' ? 'Entrepreneur Details' : 'Sponsor / Fund Parameters'}
              </label>

              {role === 'entrepreneur' ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Primary Sector / Category</label>
                    <select
                      className="form-select"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                    >
                      <option value="AI & Machine Learning">AI & Machine Learning</option>
                      <option value="CleanTech & Energy">CleanTech & Energy</option>
                      <option value="HealthTech & Bio">HealthTech & Bio</option>
                      <option value="FinTech">FinTech</option>
                      <option value="Enterprise SaaS">Enterprise SaaS</option>
                      <option value="Hardware & Robotics">Hardware & Robotics</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Current Stage</label>
                    <select
                      className="form-select"
                      value={stage}
                      onChange={(e) => setStage(e.target.value)}
                    >
                      <option value="idea">Idea Concept</option>
                      <option value="prototype">Working Prototype</option>
                      <option value="mvp">Live MVP</option>
                      <option value="scaling">Scaling / Early Growth</option>
                    </select>
                  </div>
                </div>
              ) : (
                <>
                  <Input
                    id="organizationName"
                    label="Fund / Company / Entity Name"
                    placeholder="e.g. Apex Ventures or Independent Angel"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    helperText="Leave blank if registering as an individual private angel"
                  />

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div className="form-group">
                      <label className="form-label">Min Sponsorship (₹)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={minBudget}
                        onChange={(e) => setMinBudget(e.target.value)}
                        min={100}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Max Sponsorship (₹)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={maxBudget}
                        onChange={(e) => setMaxBudget(e.target.value)}
                        min={1000}
                      />
                    </div>
                  </div>
                </>
              )}
            </div>

            <Button
              type="submit"
              variant={role === 'sponsor' ? 'emerald' : 'primary'}
              size="lg"
              isLoading={isLoading}
              style={{ width: '100%', marginBottom: 18 }}
            >
              Complete Registration & Access Dashboard
            </Button>
          </form>

          <div style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
            Already have a Vynk account?{' '}
            <Link to="/login" style={{ color: 'var(--brand-cyan)', fontWeight: 600 }}>
              Sign In here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
