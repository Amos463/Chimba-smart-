"""Add explicit assay QA/QC roles and control metadata."""
from alembic import op
import sqlalchemy as sa
revision='0004_assay_qaqc'
down_revision='0003_samples_assays'
branch_labels=None
depends_on=None
def upgrade():
    op.add_column('assays', sa.Column('qa_role', sa.String(length=20), nullable=False, server_default='primary'))
    op.add_column('assays', sa.Column('certified_value', sa.Float(), nullable=True))
    op.add_column('assays', sa.Column('duplicate_of_sample_id', sa.String(length=80), nullable=True))
    op.add_column('assays', sa.Column('tolerance_pct', sa.Float(), nullable=False, server_default='10.0'))
    op.add_column('assays', sa.Column('batch_id', sa.String(length=100), nullable=True))
def downgrade():
    op.drop_column('assays', 'batch_id')
    op.drop_column('assays', 'tolerance_pct')
    op.drop_column('assays', 'duplicate_of_sample_id')
    op.drop_column('assays', 'certified_value')
    op.drop_column('assays', 'qa_role')
