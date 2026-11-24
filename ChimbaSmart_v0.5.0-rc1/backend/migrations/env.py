from logging.config import fileConfig
from sqlalchemy import engine_from_config,pool
from alembic import context
from app.db import Base
from app import models
config=context.config
from app.config import DATABASE_URL
config.set_main_option('sqlalchemy.url',DATABASE_URL.replace('%','%%'))  # awali ilikuwa SQLite iliyoandikwa ndani ya alembic.ini
if config.config_file_name: fileConfig(config.config_file_name)
target_metadata=Base.metadata
def include_object(obj,name,type_,reflected,compare_to):
    # geom and its GiST indexes are managed by PostGIS migrations, not ORM metadata.
    if reflected and type_=='column' and name=='geom' and getattr(getattr(obj,'table',None),'name',None) in ('collars','orientations','samples'):
        return False
    if reflected and type_=='index' and name and name.endswith('_geom'):
        return False
    return True
def run_migrations_offline():
 context.configure(url=config.get_main_option('sqlalchemy.url'),target_metadata=target_metadata,include_object=include_object,literal_binds=True,dialect_opts={'paramstyle':'named'})
 with context.begin_transaction(): context.run_migrations()
def run_migrations_online():
 connectable=engine_from_config(config.get_section(config.config_ini_section),prefix='sqlalchemy.',poolclass=pool.NullPool)
 with connectable.connect() as connection:
  context.configure(connection=connection,target_metadata=target_metadata,include_object=include_object)
  with context.begin_transaction(): context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
