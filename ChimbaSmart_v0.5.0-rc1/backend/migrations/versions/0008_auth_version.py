"""Invalidate access tokens after session or password changes."""
from alembic import op
import sqlalchemy as sa

revision='0008_auth_version'
down_revision='0007_security_sessions'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column(
        'users',
        sa.Column('auth_version', sa.Integer(), server_default='0', nullable=False),
    )


def downgrade():
    op.drop_column('users','auth_version')
