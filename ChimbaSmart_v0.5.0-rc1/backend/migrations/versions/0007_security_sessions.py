"""Add refresh sessions, password reset tokens and audit events."""
from alembic import op
import sqlalchemy as sa

revision='0007_security_sessions'
down_revision='0006_attachment_dedupe'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table(
        'refresh_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_refresh_sessions_user_id', 'refresh_sessions', ['user_id'])
    op.create_index('ix_refresh_sessions_token_hash', 'refresh_sessions', ['token_hash'], unique=True)
    op.create_index('ix_refresh_sessions_user', 'refresh_sessions', ['user_id'])

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'], unique=True)

    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('actor_id', sa.String(36), nullable=True),
        sa.Column('project_id', sa.String(36), nullable=True),
        sa.Column('action', sa.String(80), nullable=False),
        sa.Column('resource_type', sa.String(80), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('outcome', sa.String(20), nullable=False),
        sa.Column('ip_address', sa.String(64), nullable=True),
        sa.Column('request_id', sa.String(100), nullable=True),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_events_project_id', 'audit_events', ['project_id'])
    op.create_index('ix_audit_project_created', 'audit_events', ['project_id', 'created_at'])


def downgrade():
    op.drop_index('ix_audit_project_created', table_name='audit_events')
    op.drop_index('ix_audit_events_project_id', table_name='audit_events')
    op.drop_table('audit_events')
    op.drop_index('ix_password_reset_tokens_token_hash', table_name='password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_user_id', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('ix_refresh_sessions_user_id', table_name='refresh_sessions')
    op.drop_index('ix_refresh_sessions_user', table_name='refresh_sessions')
    op.drop_index('ix_refresh_sessions_token_hash', table_name='refresh_sessions')
    op.drop_table('refresh_sessions')
