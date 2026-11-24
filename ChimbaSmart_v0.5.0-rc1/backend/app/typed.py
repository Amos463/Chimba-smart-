"""Typed geological records and server-side QA validation."""
from typing import Literal
from pydantic import BaseModel,Field,ValidationError,model_validator
from sqlalchemy import and_
from .models import Collar,Survey,Interval,Orientation,Sample,Assay
class CollarIn(BaseModel):
 hole_id:str=Field(min_length=1,max_length=40); kind:Literal['hole','pit','trench']='pit'
 lat:float=Field(ge=-90,le=90); lon:float=Field(ge=-180,le=180); elevation_m:float|None=None
 depth_m:float=Field(gt=0,le=3000); gps_accuracy_m:float|None=Field(None,ge=0); crs:Literal['EPSG:4326']='EPSG:4326'
class SurveyIn(BaseModel):
 hole_id:str=Field(min_length=1,max_length=40); depth_m:float=Field(ge=0); azimuth_deg:float=Field(ge=0,le=360); dip_deg:float=Field(ge=-90,le=90)
class IntervalIn(BaseModel):
 hole_id:str=Field(min_length=1,max_length=40); from_m:float=Field(ge=0); to_m:float; kind:Literal['assay','lithology']
 value_num:float|None=Field(None,ge=0); value_text:str|None=Field(None,max_length=200); unit:str='g/t'
 @model_validator(mode='after')
 def chk(self):
  if self.to_m<=self.from_m: raise ValueError('to_m lazima izidi from_m')
  if self.kind=='assay' and self.value_num is None: raise ValueError('assay inahitaji value_num')
  if self.kind=='lithology' and not self.value_text: raise ValueError('lithology inahitaji value_text')
  return self
class OrientationIn(BaseModel):
 lat:float=Field(ge=-90,le=90); lon:float=Field(ge=-180,le=180); strike_deg:float=Field(ge=0,le=360); dip_deg:float=Field(ge=0,le=90)
 kind:Literal['compass','compass_phone','surveyed']='compass'
class SampleIn(BaseModel):
 sample_id:str=Field(min_length=1,max_length=80); sample_type:Literal['rock_chip','soil','stream_sediment','channel','surface']='rock_chip'
 lat:float=Field(ge=-90,le=90); lon:float=Field(ge=-180,le=180); elevation_m:float|None=None
 gps_accuracy_m:float|None=Field(None,ge=0); lithology:str|None=Field(None,max_length=200)
 description:str|None=Field(None,max_length=2000); location_method:str='phone_gps'
class AssayIn(BaseModel):
 sample_id:str=Field(min_length=1,max_length=80); value_num:float=Field(ge=0); unit:str=Field(default='g/t',max_length=20)
 lab_name:str|None=Field(None,max_length=160); certificate_ref:str|None=Field(None,max_length=120); method:str|None=Field(None,max_length=120); detection_limit:float|None=Field(None,ge=0)
 qa_role:Literal['primary','blank','standard','duplicate']='primary'
 below_detection:bool=False
 certified_value:float|None=Field(None,gt=0); duplicate_of_sample_id:str|None=Field(None,max_length=80)
 tolerance_pct:float=Field(default=10,gt=0,le=100); batch_id:str|None=Field(None,max_length=100)
 @model_validator(mode='after')
 def qa_fields(self):
  if self.below_detection and self.detection_limit is None: raise ValueError('below_detection inahitaji detection_limit')
  if self.below_detection and self.value_num>self.detection_limit: raise ValueError('Matokeo yaliyowekwa below_detection yanazidi detection_limit')
  if self.qa_role=='standard' and self.certified_value is None: raise ValueError('standard inahitaji certified_value')
  if self.qa_role=='duplicate' and not self.duplicate_of_sample_id: raise ValueError('duplicate inahitaji duplicate_of_sample_id')
  if self.qa_role!='standard' and self.certified_value is not None: raise ValueError('certified_value ni ya standard tu')
  return self
SCHEMAS={'collar':CollarIn,'survey':SurveyIn,'interval':IntervalIn,'orientation':OrientationIn,'sample':SampleIn,'assay':AssayIn}
PRIORITY={'collar':0,'sample':0,'survey':1,'interval':2,'assay':3,'orientation':4}
def project(db,item):
 M=SCHEMAS.get(item.record_type)
 if not M: return None
 try: d=M.model_validate(item.payload)
 except ValidationError as e: return ('; '.join(f"{'.'.join(map(str,x['loc']))}: {x['msg']}" for x in e.errors()[:3]),False)
 pid,u=item.project_id,item.record_uuid
 if item.record_type=='orientation':
  db.add(Orientation(project_id=pid,record_uuid=u,lat=d.lat,lon=d.lon,strike_deg=d.strike_deg,dip_deg=d.dip_deg,kind=d.kind)); db.flush(); return None
 if item.record_type=='sample':
  sid=d.sample_id.strip().upper()
  if db.query(Sample).filter_by(project_id=pid,sample_id=sid).first(): return ('Namba ya sampuli tayari ipo kwenye mradi',False)
  db.add(Sample(project_id=pid,record_uuid=u,sample_id=sid,sample_type=d.sample_type,lat=d.lat,lon=d.lon,elevation_m=d.elevation_m,gps_accuracy_m=d.gps_accuracy_m,lithology=d.lithology,description=d.description,location_method=d.location_method)); db.flush(); return None
 if item.record_type=='assay':
  sid=d.sample_id.strip().upper()
  if not db.query(Sample).filter_by(project_id=pid,sample_id=sid).first(): return ('Sampuli haipo bado; tuma sampuli kwanza',True)
  if d.qa_role=='duplicate' and d.duplicate_of_sample_id.strip().upper()==sid: return ('Duplicate haiwezi kujirejelea yenyewe',False)
  if d.qa_role=='duplicate' and not db.query(Sample).filter_by(project_id=pid,sample_id=d.duplicate_of_sample_id.strip().upper()).first():
   return ('Sampuli ya kulinganisha duplicate haipo',True)
  db.add(Assay(project_id=pid,record_uuid=u,sample_id=sid,value_num=d.value_num,unit=d.unit,lab_name=d.lab_name,certificate_ref=d.certificate_ref,method=d.method,detection_limit=d.detection_limit,qa_role=d.qa_role,certified_value=d.certified_value,duplicate_of_sample_id=d.duplicate_of_sample_id.strip().upper() if d.duplicate_of_sample_id else None,tolerance_pct=d.tolerance_pct,batch_id=d.batch_id,below_detection=d.below_detection)); db.flush(); return None
 hid=d.hole_id.strip().upper()
 if item.record_type=='collar':
  if db.query(Collar).filter_by(project_id=pid,hole_id=hid).first(): return ('Namba ya shimo tayari ipo kwenye mradi',False)
  db.add(Collar(project_id=pid,record_uuid=u,hole_id=hid,kind=d.kind,lat=d.lat,lon=d.lon,elevation_m=d.elevation_m,depth_m=d.depth_m,gps_accuracy_m=d.gps_accuracy_m)); db.flush(); return None
 c=db.query(Collar).filter_by(project_id=pid,hole_id=hid).first()
 if not c: return ('Collar haipo bado; tuma collar kwanza',True)
 if item.record_type=='survey':
  if d.depth_m>c.depth_m+1e-6: return ('Kina cha survey kinazidi urefu wa shimo',False)
  db.add(Survey(project_id=pid,record_uuid=u,hole_id=hid,depth_m=d.depth_m,azimuth_deg=d.azimuth_deg,dip_deg=d.dip_deg)); db.flush(); return None
 if d.to_m>c.depth_m+1e-6: return ('Kipande kinazidi urefu wa shimo',False)
 if db.query(Interval).filter(and_(Interval.project_id==pid,Interval.hole_id==hid,Interval.kind==d.kind,Interval.from_m<d.to_m,Interval.to_m>d.from_m)).first(): return ('Vipande vya aina moja vinagongana',False)
 db.add(Interval(project_id=pid,record_uuid=u,hole_id=hid,from_m=d.from_m,to_m=d.to_m,kind=d.kind,value_num=d.value_num,value_text=d.value_text,unit=d.unit)); db.flush(); return None
