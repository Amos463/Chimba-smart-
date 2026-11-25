"""Add auditable project and batch QA waivers."""
from alembic import op
import sqlalchemy as sa

revision='0009_qa_waivers'
down_revision='0008_auth_version'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table(
        'qa_waivers',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('project_id',sa.String(36),nullable=False),
        sa.Column('batch_id',sa.String(100),nullable=True),
        sa.Column('reason',sa.Text(),nullable=False),
        sa.Column('created_by',sa.String(36),nullable=False),
        sa.Column('created_by_username',sa.String(100),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('revoked_at',sa.DateTime(timezone=True),nullable=True),
        sa.Column('revoked_by',sa.String(36),nullable=True),
    )
    op.create_index('ix_qa_waivers_project_id','qa_waivers',['project_id'])
    op.create_index('ix_qa_waivers_active','qa_waivers',['project_id','revoked_at'])


def downgrade():
    op.drop_index('ix_qa_waivers_active',table_name='qa_waivers')
    op.drop_index('ix_qa_waivers_project_id',table_name='qa_waivers')
    op.drop_table('qa_waivers')
