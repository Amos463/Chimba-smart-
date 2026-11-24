from sqlalchemy import String,Text,DateTime,Integer,Float,ForeignKey,UniqueConstraint,Index,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime,timezone
from .db import Base
def utcnow(): return datetime.now(timezone.utc)
S=lambda n=36,**k: mapped_column(String(n),**k)
class User(Base):
    __tablename__='users'
    id:Mapped[str]=S(primary_key=True); username:Mapped[str]=S(100,unique=True,index=True)
    password_hash:Mapped[str]=S(255); role:Mapped[str]=S(40,default='field_user')
class Project(Base):
    __tablename__='projects'
    id:Mapped[str]=S(primary_key=True); name:Mapped[str]=S(200)
    projected_crs:Mapped[str]=S(40,default='auto')  # 'auto' (WGS84 UTM), 'arc1960', au 'EPSG:xxxxx'
    created_by:Mapped[str]=S(); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class ProjectMember(Base):
    __tablename__='project_members'
    project_id:Mapped[str]=S(primary_key=True); user_id:Mapped[str]=S(primary_key=True); role:Mapped[str]=S(20,default='member')
class Record(Base):
    __tablename__='records'
    __table_args__=(UniqueConstraint('project_id','record_uuid',name='uq_project_record'),Index('ix_records_sync','project_id','updated_at_utc'))
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(); record_type:Mapped[str]=S(80)
    payload_json:Mapped[str]=mapped_column(Text)
    created_at_utc:Mapped[datetime]=mapped_column(DateTime(timezone=True)); updated_at_utc:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    created_by:Mapped[str]=S(); device_id:Mapped[str]=S(100); source_method:Mapped[str]=S(100)
    crs:Mapped[str|None]=S(100,nullable=True)
    content_hash:Mapped[str]=S(64)            # SHA-256 iliyokokotolewa na SEVA (chanzo cha ukweli)
    client_hash:Mapped[str|None]=S(64,nullable=True)  # ya mteja, ushauri tu
    server_version:Mapped[int]=mapped_column(Integer,default=1)
    deleted_at_utc:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
class SyncConflict(Base):
    __tablename__='sync_conflicts'
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(index=True); device_id:Mapped[str]=S(100)
    incoming_json:Mapped[str]=mapped_column(Text); existing_json:Mapped[str]=mapped_column(Text)
    created_at_utc:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow); resolution:Mapped[str]=S(30,default='unresolved')
class _Typed:
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
class Collar(_Typed,Base):
    __tablename__='collars'; __table_args__=(UniqueConstraint('project_id','hole_id',name='uq_collar_hole'),)
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True); hole_id:Mapped[str]=S(40); kind:Mapped[str]=S(20)
    lat:Mapped[float]=mapped_column(Float); lon:Mapped[float]=mapped_column(Float)
    elevation_m:Mapped[float|None]=mapped_column(Float,nullable=True); depth_m:Mapped[float]=mapped_column(Float)
    gps_accuracy_m:Mapped[float|None]=mapped_column(Float,nullable=True)
class Survey(_Typed,Base):
    __tablename__='surveys'
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True); hole_id:Mapped[str]=S(40,index=True)
    depth_m:Mapped[float]=mapped_column(Float); azimuth_deg:Mapped[float]=mapped_column(Float); dip_deg:Mapped[float]=mapped_column(Float)
class Interval(_Typed,Base):
    __tablename__='intervals'
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True); hole_id:Mapped[str]=S(40,index=True)
    from_m:Mapped[float]=mapped_column(Float); to_m:Mapped[float]=mapped_column(Float); kind:Mapped[str]=S(20)
    value_num:Mapped[float|None]=mapped_column(Float,nullable=True); value_text:Mapped[str|None]=S(200,nullable=True); unit:Mapped[str]=S(20,default='g/t')
class Orientation(_Typed,Base):
    __tablename__='orientations'
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True)
    lat:Mapped[float]=mapped_column(Float); lon:Mapped[float]=mapped_column(Float)
    strike_deg:Mapped[float]=mapped_column(Float); dip_deg:Mapped[float]=mapped_column(Float); kind:Mapped[str]=S(30,default='compass')
class Job(Base):
    __tablename__='jobs'
    id:Mapped[str]=S(primary_key=True); project_id:Mapped[str]=S(index=True); engine:Mapped[str]=S(40); engine_version:Mapped[str|None]=S(40,nullable=True)
    params_json:Mapped[str]=mapped_column(Text,default='{}'); input_hash:Mapped[str|None]=S(64,nullable=True)
    status:Mapped[str]=S(20,default='queued')  # queued|running|done|rejected|failed
    result_json:Mapped[str|None]=mapped_column(Text,nullable=True); warnings_json:Mapped[str|None]=mapped_column(Text,nullable=True); error:Mapped[str|None]=mapped_column(Text,nullable=True)
    requested_by:Mapped[str]=S(); review_state:Mapped[str]=S(20,default='unreviewed')
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    started_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True); finished_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)


class Sample(Base):
    """Sampuli ya eneo huru; si collar ya drillhole."""
    __tablename__='samples'
    __table_args__=(UniqueConstraint('project_id','sample_id',name='uq_project_sample'),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True)
    sample_id:Mapped[str]=S(80); sample_type:Mapped[str]=S(40)
    lat:Mapped[float]=mapped_column(Float); lon:Mapped[float]=mapped_column(Float)
    elevation_m:Mapped[float|None]=mapped_column(Float,nullable=True)
    gps_accuracy_m:Mapped[float|None]=mapped_column(Float,nullable=True)
    lithology:Mapped[str|None]=S(200,nullable=True); description:Mapped[str|None]=mapped_column(Text,nullable=True)
    location_method:Mapped[str]=S(40,default='phone_gps')

class Assay(Base):
    """Matokeo ya maabara yanayoweza kuongezwa baada ya sampuli."""
    __tablename__='assays'
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    project_id:Mapped[str]=S(index=True); record_uuid:Mapped[str]=S(unique=True)
    sample_id:Mapped[str]=S(80,index=True); value_num:Mapped[float]=mapped_column(Float)
    unit:Mapped[str]=S(20,default='g/t'); lab_name:Mapped[str|None]=S(160,nullable=True)
    certificate_ref:Mapped[str|None]=S(120,nullable=True); method:Mapped[str|None]=S(120,nullable=True)
    detection_limit:Mapped[float|None]=mapped_column(Float,nullable=True)
    qa_role:Mapped[str]=S(20,default='primary')
    below_detection:Mapped[bool]=mapped_column(Boolean,default=False)
    certified_value:Mapped[float|None]=mapped_column(Float,nullable=True)
    duplicate_of_sample_id:Mapped[str|None]=S(80,nullable=True)
    tolerance_pct:Mapped[float]=mapped_column(Float,default=10.0)
    batch_id:Mapped[str|None]=S(100,nullable=True)


class Attachment(Base):
    __tablename__='attachments'
    __table_args__=(UniqueConstraint('project_id','sample_id','sha256',name='uq_attachment_sample_hash'),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    project_id:Mapped[str]=S(index=True); sample_id:Mapped[str]=S(80,index=True); sample_record_uuid:Mapped[str]=S(36,index=True)
    storage_key:Mapped[str]=S(80,unique=True); filename:Mapped[str]=S(255)
    media_type:Mapped[str]=S(80); sha256:Mapped[str]=S(64); size_bytes:Mapped[int]=mapped_column(Integer)
    uploaded_by:Mapped[str]=S(); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)


class RefreshSession(Base):
    __tablename__='refresh_sessions'
    __table_args__=(Index('ix_refresh_sessions_user','user_id'),)
    id:Mapped[str]=S(primary_key=True)
    user_id:Mapped[str]=S(36,index=True)
    token_hash:Mapped[str]=S(64,unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    revoked_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    replaced_by:Mapped[str|None]=S(36,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)


class PasswordResetToken(Base):
    __tablename__='password_reset_tokens'
    id:Mapped[str]=S(primary_key=True)
    user_id:Mapped[str]=S(36,index=True)
    token_hash:Mapped[str]=S(64,unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    used_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)


class AuditEvent(Base):
    __tablename__='audit_events'
    __table_args__=(Index('ix_audit_project_created','project_id','created_at'),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    actor_id:Mapped[str|None]=S(36,nullable=True)
    project_id:Mapped[str|None]=S(36,nullable=True,index=True)
    action:Mapped[str]=S(80)
    resource_type:Mapped[str|None]=S(80,nullable=True)
    resource_id:Mapped[str|None]=S(100,nullable=True)
    outcome:Mapped[str]=S(20)
    ip_address:Mapped[str|None]=S(64,nullable=True)
    request_id:Mapped[str|None]=S(100,nullable=True)
    details_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
