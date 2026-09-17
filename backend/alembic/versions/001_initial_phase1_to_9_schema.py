"""Baseline Phase 1 to Phase 9 schema migration for PostgreSQL

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-09-17 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_suspended', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('suspended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('suspended_by', sa.Integer(), nullable=True),
        sa.Column('suspension_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['suspended_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # 2. entrepreneur_profiles
    op.create_table(
        'entrepreneur_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False, server_default='idea'),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=False),
        sa.Column('experience', sa.JSON(), nullable=False),
        sa.Column('education', sa.JSON(), nullable=False),
        sa.Column('achievements', sa.JSON(), nullable=False),
        sa.Column('pitch_deck_url', sa.String(length=512), nullable=True),
        sa.Column('linkedin_url', sa.String(length=512), nullable=True),
        sa.Column('github_url', sa.String(length=512), nullable=True),
        sa.Column('website_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_entrepreneur_profiles_id'), 'entrepreneur_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_entrepreneur_profiles_user_id'), 'entrepreneur_profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_entrepreneur_profiles_industry'), 'entrepreneur_profiles', ['industry'], unique=False)

    # 3. sponsor_profiles
    op.create_table(
        'sponsor_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_name', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('about', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('sponsor_type', sa.String(length=100), nullable=False, server_default='individual_angel'),
        sa.Column('focus_industries', sa.JSON(), nullable=False),
        sa.Column('min_budget', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('max_budget', sa.Integer(), nullable=False, server_default='50000'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('preferred_sponsorship_types', sa.JSON(), nullable=False),
        sa.Column('sponsorship_interests', sa.JSON(), nullable=False),
        sa.Column('areas_supported', sa.JSON(), nullable=False),
        sa.Column('previous_collaborations', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_sponsor_profiles_id'), 'sponsor_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_sponsor_profiles_user_id'), 'sponsor_profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_sponsor_profiles_industry'), 'sponsor_profiles', ['industry'], unique=False)

    # 4. projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entrepreneur_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('tagline', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=False, server_default='idea'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('problem_statement', sa.Text(), nullable=True),
        sa.Column('proposed_solution', sa.Text(), nullable=True),
        sa.Column('target_market', sa.Text(), nullable=True),
        sa.Column('value_proposition', sa.Text(), nullable=True),
        sa.Column('current_progress', sa.Text(), nullable=True),
        sa.Column('funding_goal', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('funding_received', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('required_support', sa.JSON(), nullable=False),
        sa.Column('required_resources', sa.Text(), nullable=True),
        sa.Column('skills_needed', sa.JSON(), nullable=False),
        sa.Column('tech_stack', sa.JSON(), nullable=False),
        sa.Column('website_url', sa.String(length=512), nullable=True),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('video_url', sa.String(length=512), nullable=True),
        sa.Column('cover_image_url', sa.String(length=512), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('timeline', sa.String(length=255), nullable=True),
        sa.Column('moderation_status', sa.String(length=50), nullable=False, server_default='approved'),
        sa.Column('moderation_reason', sa.Text(), nullable=True),
        sa.Column('moderated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('moderated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['entrepreneur_id'], ['entrepreneur_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_entrepreneur_id'), 'projects', ['entrepreneur_id'], unique=False)
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=True)
    op.create_index(op.f('ix_projects_category'), 'projects', ['category'], unique=False)
    op.create_index(op.f('ix_projects_stage'), 'projects', ['stage'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)

    # 5. project_requirements
    op.create_table(
        'project_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('requirement_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_budget', sa.Float(), nullable=True),
        sa.Column('is_fulfilled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_requirements_id'), 'project_requirements', ['id'], unique=False)
    op.create_index(op.f('ix_project_requirements_project_id'), 'project_requirements', ['project_id'], unique=False)

    # 6. sponsorship_requests
    op.create_table(
        'sponsorship_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('requested_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('sponsorship_type', sa.String(length=50), nullable=False, server_default='financial'),
        sa.Column('requested_resources', sa.Text(), nullable=True),
        sa.Column('deliverables', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('response_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sponsorship_requests_id'), 'sponsorship_requests', ['id'], unique=False)
    op.create_index(op.f('ix_sponsorship_requests_sender_id'), 'sponsorship_requests', ['sender_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_requests_recipient_id'), 'sponsorship_requests', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_requests_project_id'), 'sponsorship_requests', ['project_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_requests_status'), 'sponsorship_requests', ['status'], unique=False)

    # 7. sponsorship_commitments
    op.create_table(
        'sponsorship_commitments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('sponsor_id', sa.Integer(), nullable=False),
        sa.Column('entrepreneur_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('sponsorship_type', sa.String(length=50), nullable=False, server_default='financial'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='interested'),
        sa.Column('next_action_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('follow_up_reason', sa.String(length=255), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('cancellation_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['request_id'], ['sponsorship_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sponsor_id'], ['sponsor_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['entrepreneur_id'], ['entrepreneur_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sponsorship_commitments_id'), 'sponsorship_commitments', ['id'], unique=False)
    op.create_index(op.f('ix_sponsorship_commitments_request_id'), 'sponsorship_commitments', ['request_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_commitments_sponsor_id'), 'sponsorship_commitments', ['sponsor_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_commitments_entrepreneur_id'), 'sponsorship_commitments', ['entrepreneur_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_commitments_project_id'), 'sponsorship_commitments', ['project_id'], unique=False)
    op.create_index(op.f('ix_sponsorship_commitments_status'), 'sponsorship_commitments', ['status'], unique=False)

    # 8. commitment_updates
    op.create_table(
        'commitment_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commitment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('from_status', sa.String(length=50), nullable=True),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False, server_default='status_change'),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('cancellation_type', sa.String(length=50), nullable=True),
        sa.Column('evidence_reference', sa.String(length=512), nullable=True),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['commitment_id'], ['sponsorship_commitments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_commitment_updates_id'), 'commitment_updates', ['id'], unique=False)
    op.create_index(op.f('ix_commitment_updates_commitment_id'), 'commitment_updates', ['commitment_id'], unique=False)

    # 9. trust_scores
    op.create_table(
        'trust_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('score_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('verification_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('commitments_points', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('responsiveness_points', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('activity_points', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('completed_commitments_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cancelled_commitments_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_milestones_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_hours', sa.Float(), nullable=False, server_default='24.0'),
        sa.Column('last_calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_trust_scores_id'), 'trust_scores', ['id'], unique=False)
    op.create_index(op.f('ix_trust_scores_user_id'), 'trust_scores', ['user_id'], unique=True)

    # 10. trust_score_events
    op.create_table(
        'trust_score_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('score_before', sa.Integer(), nullable=True),
        sa.Column('score_after', sa.Integer(), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trust_score_events_id'), 'trust_score_events', ['id'], unique=False)
    op.create_index(op.f('ix_trust_score_events_user_id'), 'trust_score_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_trust_score_events_event_type'), 'trust_score_events', ['event_type'], unique=False)

    # 11. conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_a_id', sa.Integer(), nullable=False),
        sa.Column('participant_b_id', sa.Integer(), nullable=False),
        sa.Column('sponsorship_request_id', sa.Integer(), nullable=True),
        sa.Column('commitment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['participant_a_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_b_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sponsorship_request_id'], ['sponsorship_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['commitment_id'], ['sponsorship_commitments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_participant_a_id'), 'conversations', ['participant_a_id'], unique=False)
    op.create_index(op.f('ix_conversations_participant_b_id'), 'conversations', ['participant_b_id'], unique=False)

    # 12. messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_recipient_id'), 'messages', ['recipient_id'], unique=False)

    # 13. notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='system'),
        sa.Column('link', sa.String(length=512), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # 14. notification_preferences
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_marketing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_messages', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_sponsorship', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_trust_score', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_notification_preferences_id'), 'notification_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_notification_preferences_user_id'), 'notification_preferences', ['user_id'], unique=True)

    # 15. verification_records
    op.create_table(
        'verification_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('verification_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('document_url', sa.String(length=512), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_records_id'), 'verification_records', ['id'], unique=False)
    op.create_index(op.f('ix_verification_records_user_id'), 'verification_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_verification_records_status'), 'verification_records', ['status'], unique=False)

    # 16. reports
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('reported_user_id', sa.Integer(), nullable=True),
        sa.Column('reported_project_id', sa.Integer(), nullable=True),
        sa.Column('reported_sponsorship_request_id', sa.Integer(), nullable=True),
        sa.Column('reported_commitment_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='other'),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reported_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reported_project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reported_sponsorship_request_id'], ['sponsorship_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reported_commitment_id'], ['sponsorship_commitments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_reporter_id'), 'reports', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)

    # 17. disputes
    op.create_table(
        'disputes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commitment_id', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('initiator_id', sa.Integer(), nullable=False),
        sa.Column('respondent_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['commitment_id'], ['sponsorship_commitments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['request_id'], ['sponsorship_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['initiator_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['respondent_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disputes_id'), 'disputes', ['id'], unique=False)
    op.create_index(op.f('ix_disputes_status'), 'disputes', ['status'], unique=False)

    # 18. admin_audit_logs
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_audit_logs_id'), 'admin_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_action'), 'admin_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_entity_type'), 'admin_audit_logs', ['entity_type'], unique=False)

    # 19. ai_match_explanations
    op.create_table(
        'ai_match_explanations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('sponsor_id', sa.Integer(), nullable=False),
        sa.Column('compatibility_score', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False),
        sa.Column('alignment_areas', sa.JSON(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='gemini'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sponsor_id'], ['sponsor_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_match_explanations_id'), 'ai_match_explanations', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('ai_match_explanations')
    op.drop_table('admin_audit_logs')
    op.drop_table('disputes')
    op.drop_table('reports')
    op.drop_table('verification_records')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('trust_score_events')
    op.drop_table('trust_scores')
    op.drop_table('commitment_updates')
    op.drop_table('sponsorship_commitments')
    op.drop_table('sponsorship_requests')
    op.drop_table('project_requirements')
    op.drop_table('projects')
    op.drop_table('sponsor_profiles')
    op.drop_table('entrepreneur_profiles')
    op.drop_table('users')
