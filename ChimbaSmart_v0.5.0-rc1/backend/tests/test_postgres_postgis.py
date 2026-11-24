"""Run only against a disposable PostgreSQL/PostGIS test database."""
import os
import pytest
from sqlalchemy import create_engine, inspect, text

@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"), reason="TEST_POSTGRES_URL haijawekwa")
def test_postgres_postgis_migrations():
    url=os.environ["TEST_POSTGRES_URL"]
    os.environ["DATABASE_URL"]=url
    from app import config as app_config
    app_config.DATABASE_URL=url
    from alembic.config import Config
    from alembic import command
    cfg=Config(os.path.join(os.path.dirname(__file__),"..","alembic.ini"))
    command.upgrade(cfg,"head")
    engine=create_engine(url)
    try:
        insp=inspect(engine)
        for table in ("users","projects","samples","assays","attachments","records"):
            assert table in insp.get_table_names()
        cols={c["name"] for c in insp.get_columns("samples")}
        assert "geom" in cols
        assert "geom" in {c["name"] for c in insp.get_columns("collars")}
        assert "geom" in {c["name"] for c in insp.get_columns("orientations")}
        with engine.connect() as conn:
            assert conn.execute(text("SELECT PostGIS_Full_Version()")).scalar()
    finally:
        engine.dispose()
