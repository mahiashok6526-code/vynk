-- ==============================================================================
-- Vynk — Production PostgreSQL DDL Schema for Supabase
-- Covers all Phase 1 through Phase 9 models and indexes
-- Generated from Alembic baseline revision: 001_initial_schema
-- ==============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    avatar_url VARCHAR(512),
    headline VARCHAR(255),
    bio TEXT,
    location VARCHAR(255),
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    suspended_at TIMESTAMPTZ,
    suspended_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    suspension_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);

-- 2. Entrepreneur Profiles Table
CREATE TABLE IF NOT EXISTS entrepreneur_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stage VARCHAR(50) NOT NULL DEFAULT 'idea',
    industry VARCHAR(100),
    skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    experience JSONB NOT NULL DEFAULT '[]'::jsonb,
    education JSONB NOT NULL DEFAULT '[]'::jsonb,
    achievements JSONB NOT NULL DEFAULT '[]'::jsonb,
    social_links JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_entrepreneur_profiles_id ON entrepreneur_profiles(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_entrepreneur_profiles_user_id ON entrepreneur_profiles(user_id);

-- 3. Sponsor Profiles Table
CREATE TABLE IF NOT EXISTS sponsor_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_name VARCHAR(255),
    sponsor_type VARCHAR(50) NOT NULL DEFAULT 'individual_sponsor',
    logo_url VARCHAR(512),
    about TEXT,
    industry VARCHAR(100),
    focus_industries JSONB NOT NULL DEFAULT '[]'::jsonb,
    preferred_stages JSONB NOT NULL DEFAULT '[]'::jsonb,
    sponsorship_types JSONB NOT NULL DEFAULT '[]'::jsonb,
    sponsorship_interests JSONB NOT NULL DEFAULT '[]'::jsonb,
    areas_supported JSONB NOT NULL DEFAULT '[]'::jsonb,
    previous_collaborations JSONB NOT NULL DEFAULT '[]'::jsonb,
    min_budget FLOAT NOT NULL DEFAULT 1000.0,
    max_budget FLOAT NOT NULL DEFAULT 100000.0,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    website_url VARCHAR(512),
    social_links JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sponsor_profiles_id ON sponsor_profiles(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_sponsor_profiles_user_id ON sponsor_profiles(user_id);

-- 4. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    entrepreneur_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    tagline VARCHAR(255),
    description TEXT,
    category VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    stage VARCHAR(50) NOT NULL DEFAULT 'idea',
    problem_statement TEXT,
    proposed_solution TEXT,
    target_market TEXT,
    value_proposition TEXT,
    current_progress TEXT,
    funding_goal FLOAT NOT NULL DEFAULT 0.0,
    funding_received FLOAT NOT NULL DEFAULT 0.0,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    required_support JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_resources TEXT,
    skills_needed JSONB NOT NULL DEFAULT '[]'::jsonb,
    tech_stack JSONB NOT NULL DEFAULT '[]'::jsonb,
    website_url VARCHAR(512),
    pitch_deck_url VARCHAR(512),
    demo_url VARCHAR(512),
    logo_url VARCHAR(512),
    video_url VARCHAR(512),
    cover_image_url VARCHAR(512),
    location VARCHAR(255),
    timeline VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    moderation_status VARCHAR(50) NOT NULL DEFAULT 'approved',
    moderation_reason TEXT,
    moderated_at TIMESTAMPTZ,
    moderated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_projects_id ON projects(id);
CREATE INDEX IF NOT EXISTS ix_projects_entrepreneur_id ON projects(entrepreneur_id);
CREATE INDEX IF NOT EXISTS ix_projects_category ON projects(category);
CREATE INDEX IF NOT EXISTS ix_projects_stage ON projects(stage);
CREATE INDEX IF NOT EXISTS ix_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS ix_projects_moderation_status ON projects(moderation_status);

-- 5. Sponsorship Requests Table
CREATE TABLE IF NOT EXISTS sponsorship_requests (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entrepreneur_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sponsor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL DEFAULT 'monetary',
    amount FLOAT,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    requested_resources TEXT,
    message TEXT NOT NULL,
    proposal_deck_url VARCHAR(512),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    response_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sponsorship_requests_id ON sponsorship_requests(id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_requests_project_id ON sponsorship_requests(project_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_requests_entrepreneur_id ON sponsorship_requests(entrepreneur_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_requests_sponsor_id ON sponsorship_requests(sponsor_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_requests_status ON sponsorship_requests(status);

-- 6. Sponsorship Commitments Table
CREATE TABLE IF NOT EXISTS sponsorship_commitments (
    id SERIAL PRIMARY KEY,
    sponsorship_request_id INTEGER REFERENCES sponsorship_requests(id) ON DELETE SET NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sponsor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entrepreneur_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    description TEXT,
    commitment_type VARCHAR(50) NOT NULL DEFAULT 'monetary',
    amount FLOAT,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    non_monetary_details TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'interested',
    contract_reference VARCHAR(255),
    follow_up_date TIMESTAMPTZ,
    follow_up_reason VARCHAR(255),
    cancellation_type VARCHAR(50),
    cancellation_reason TEXT,
    cancelled_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sponsorship_commitments_id ON sponsorship_commitments(id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_commitments_project_id ON sponsorship_commitments(project_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_commitments_sponsor_id ON sponsorship_commitments(sponsor_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_commitments_entrepreneur_id ON sponsorship_commitments(entrepreneur_id);
CREATE INDEX IF NOT EXISTS ix_sponsorship_commitments_status ON sponsorship_commitments(status);

-- 7. Commitment Updates (Milestones) Table
CREATE TABLE IF NOT EXISTS commitment_updates (
    id SERIAL PRIMARY KEY,
    commitment_id INTEGER NOT NULL REFERENCES sponsorship_commitments(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    update_type VARCHAR(50) NOT NULL DEFAULT 'status_change',
    title VARCHAR(255),
    status_from VARCHAR(50),
    status_to VARCHAR(50),
    note TEXT,
    cancellation_type VARCHAR(50),
    evidence_reference VARCHAR(512),
    event_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_commitment_updates_id ON commitment_updates(id);
CREATE INDEX IF NOT EXISTS ix_commitment_updates_commitment_id ON commitment_updates(commitment_id);

-- 8. Trust Scores Table
CREATE TABLE IF NOT EXISTS trust_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL DEFAULT 50,
    identity_score INTEGER NOT NULL DEFAULT 50,
    reliability_score INTEGER NOT NULL DEFAULT 50,
    activity_score INTEGER NOT NULL DEFAULT 50,
    reputation_score INTEGER NOT NULL DEFAULT 50,
    score_version INTEGER NOT NULL DEFAULT 1,
    fulfilled_commitments_count INTEGER NOT NULL DEFAULT 0,
    completed_milestones_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_trust_scores_id ON trust_scores(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_trust_scores_user_id ON trust_scores(user_id);

-- 9. Trust Score Events Table
CREATE TABLE IF NOT EXISTS trust_score_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    impact INTEGER NOT NULL,
    score_before INTEGER,
    score_after INTEGER,
    reference_type VARCHAR(50),
    reference_id INTEGER,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_trust_score_events_id ON trust_score_events(id);
CREATE INDEX IF NOT EXISTS ix_trust_score_events_user_id ON trust_score_events(user_id);
CREATE INDEX IF NOT EXISTS ix_trust_score_events_event_type ON trust_score_events(event_type);

-- 10. Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    participant_a_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_b_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sponsorship_request_id INTEGER REFERENCES sponsorship_requests(id) ON DELETE SET NULL,
    commitment_id INTEGER REFERENCES sponsorship_commitments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_conversations_id ON conversations(id);
CREATE INDEX IF NOT EXISTS ix_conversations_participant_a_id ON conversations(participant_a_id);
CREATE INDEX IF NOT EXISTS ix_conversations_participant_b_id ON conversations(participant_b_id);

-- 11. Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_messages_id ON messages(id);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS ix_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS ix_messages_recipient_id ON messages(recipient_id);

-- 12. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'system',
    link VARCHAR(512),
    entity_type VARCHAR(50),
    entity_id INTEGER,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications(id);
CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);

-- 13. Notification Preferences Table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    email_marketing BOOLEAN NOT NULL DEFAULT FALSE,
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_messages BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_sponsorship BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_trust_score BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_notification_preferences_id ON notification_preferences(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_notification_preferences_user_id ON notification_preferences(user_id);

-- 14. Verification Records Table
CREATE TABLE IF NOT EXISTS verification_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    document_url VARCHAR(512),
    notes TEXT,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_verification_records_id ON verification_records(id);
CREATE INDEX IF NOT EXISTS ix_verification_records_user_id ON verification_records(user_id);
CREATE INDEX IF NOT EXISTS ix_verification_records_status ON verification_records(status);

-- 15. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reported_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    reported_sponsorship_request_id INTEGER REFERENCES sponsorship_requests(id) ON DELETE SET NULL,
    reported_commitment_id INTEGER REFERENCES sponsorship_commitments(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'other',
    reason VARCHAR(255) NOT NULL,
    details TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    resolution_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_reports_id ON reports(id);
CREATE INDEX IF NOT EXISTS ix_reports_reporter_id ON reports(reporter_id);
CREATE INDEX IF NOT EXISTS ix_reports_status ON reports(status);

-- 16. Disputes Table
CREATE TABLE IF NOT EXISTS disputes (
    id SERIAL PRIMARY KEY,
    commitment_id INTEGER REFERENCES sponsorship_commitments(id) ON DELETE SET NULL,
    request_id INTEGER REFERENCES sponsorship_requests(id) ON DELETE SET NULL,
    initiator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    respondent_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    resolution TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_disputes_id ON disputes(id);
CREATE INDEX IF NOT EXISTS ix_disputes_status ON disputes(status);

-- 17. Admin Audit Logs Table
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    description TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_id ON admin_audit_logs(id);
CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_action ON admin_audit_logs(action);
CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_entity_type ON admin_audit_logs(entity_type);

-- 18. AI Match Explanations Table
CREATE TABLE IF NOT EXISTS ai_match_explanations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sponsor_id INTEGER NOT NULL REFERENCES sponsor_profiles(id) ON DELETE CASCADE,
    compatibility_score INTEGER NOT NULL,
    explanation TEXT NOT NULL,
    strengths JSONB NOT NULL DEFAULT '[]'::jsonb,
    alignment_areas JSONB NOT NULL DEFAULT '[]'::jsonb,
    provider VARCHAR(50) NOT NULL DEFAULT 'gemini',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_ai_match_explanations_id ON ai_match_explanations(id);

-- 19. Alembic Migration Tracking Table
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);
INSERT INTO alembic_version (version_num) 
VALUES ('001_initial_schema')
ON CONFLICT (version_num) DO NOTHING;
