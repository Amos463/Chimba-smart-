"""Prevent duplicate image payloads per sample."""
from alembic import op
revision='0006_attachment_dedupe'
down_revision='0005_assay_detection_qualifier'
branch_labels=None
depends_on=None
def upgrade():
    with op.batch_alter_table('attachments') as batch:
        batch.create_unique_constraint('uq_attachment_sample_hash',['project_id','sample_id','sha256'])
def downgrade():
    with op.batch_alter_table('attachments') as batch:
        batch.drop_constraint('uq_attachment_sample_hash',type_='unique')
