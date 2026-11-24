"""Distinguish below-detection assays from numeric grade observations."""
from alembic import op
import sqlalchemy as sa
revision='0005_assay_detection_qualifier'
down_revision='0004_assay_qaqc'
branch_labels=None
depends_on=None
def upgrade():
    op.add_column('assays', sa.Column('below_detection', sa.Boolean(), nullable=False, server_default=sa.false()))
def downgrade():
    op.drop_column('assays', 'below_detection')
