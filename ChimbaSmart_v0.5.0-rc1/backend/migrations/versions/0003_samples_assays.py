"""Add PostGIS geometry for surface samples (tables are in 0001)."""
from alembic import op
revision='0003_samples_assays'
down_revision='0002_postgis'
branch_labels=None
depends_on=None
def upgrade():
    bind=op.get_bind()
    if bind.dialect.name=='postgresql':
        op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
        op.execute("ALTER TABLE samples ADD COLUMN IF NOT EXISTS geom geometry(Point,4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lon,lat),4326)) STORED")
        op.execute('CREATE INDEX IF NOT EXISTS ix_samples_geom ON samples USING GIST (geom)')
def downgrade():
    if op.get_bind().dialect.name=='postgresql':
        op.execute('DROP INDEX IF EXISTS ix_samples_geom')
        op.execute('ALTER TABLE samples DROP COLUMN IF EXISTS geom')
