from alembic import op
revision='0002_postgis'; down_revision='0001_initial'; branch_labels=None; depends_on=None
def upgrade():
    if op.get_bind().dialect.name!='postgresql': return  # SQLite dev: hakuna PostGIS
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    for t in ('collars','orientations'):
        op.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS geom geometry(Point,4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lon,lat),4326)) STORED")
        op.execute(f"CREATE INDEX IF NOT EXISTS ix_{t}_geom ON {t} USING GIST (geom)")
def downgrade():
    if op.get_bind().dialect.name!='postgresql': return
    for t in ('collars','orientations'): op.execute(f"ALTER TABLE {t} DROP COLUMN IF EXISTS geom")
