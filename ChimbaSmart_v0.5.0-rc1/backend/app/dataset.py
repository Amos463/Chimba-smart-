"""Build a CRS-explicit, provenance-hashed dataset for processing engines."""
import hashlib,json
from .models import Collar,Survey,Interval,Orientation,Sample,Assay
from . import geo
def _d(o): return {c.name:getattr(o,c.name) for c in o.__table__.columns if c.name not in ('id','record_uuid','project_id')}
def build(db,project):
 pid=project.id; q=lambda M: db.query(M).filter_by(project_id=pid).order_by(M.id).all()
 C,S,I,O,SM,A=q(Collar),q(Survey),q(Interval),q(Orientation),q(Sample),q(Assay)
 coords=[(x.lon,x.lat) for x in C]+[(x.lon,x.lat) for x in SM]
 epsg=None
 if coords:
  epsg=f"EPSG:{geo.projected_epsg(sum(x for x,y in coords)/len(coords),sum(y for x,y in coords)/len(coords),project.projected_crs)}"
 def xy(lat,lon): return geo.to_projected(lat,lon,epsg)[:2]
 assays_by={}
 for a in A: assays_by.setdefault(a.sample_id,[]).append(a)
 qa_checks=[]
 for a in A:
  role=getattr(a,'qa_role','primary') or 'primary'
  if role=='primary': continue  # primary assay si QA control record
  status='not_assessed'; detail=''
  if role=='blank':
   limit=a.detection_limit if a.detection_limit is not None else 0.0
   status='pass' if a.value_num<=limit else 'fail'; detail=f'blank={a.value_num}, limit={limit}'
  elif role=='standard':
   if a.certified_value and a.certified_value>0:
    dev=abs(a.value_num-a.certified_value)/a.certified_value*100
    status='pass' if dev<=a.tolerance_pct else 'fail'; detail=f'deviation_pct={dev:.3f}'
  elif role=='duplicate':
   refs=[x for x in A if x.sample_id==a.duplicate_of_sample_id and (getattr(x,'qa_role','primary') or 'primary')=='primary' and x.unit==a.unit]
   distinct={(x.value_num,x.unit,x.lab_name,x.certificate_ref,x.method) for x in refs}
   if len(distinct)==1 and refs:
    ref=refs[-1]; denom=(abs(a.value_num)+abs(ref.value_num))/2
    rpd=abs(a.value_num-ref.value_num)/denom*100 if denom else 0.0
    status='pass' if rpd<=a.tolerance_pct else 'fail'; detail=f'RPD_pct={rpd:.3f}'
   elif len(distinct)>1: status='not_assessed'; detail='Primary assays nyingi zinapingana; duplicate haiwezi kulinganishwa'
   else: status='pending'; detail='primary assay haijafika'
  qa_checks.append({'sample_id':a.sample_id,'role':role,'batch_id':a.batch_id,'status':status,'detail':detail,'record_uuid':a.record_uuid})
 samples=[]
 for x in SM:
  aa=assays_by.get(x.sample_id,[]); primary_assays=[a for a in aa if (getattr(a,'qa_role','primary') or 'primary')=='primary']; valid=[a for a in aa if a.unit=='g/t' and (getattr(a,'qa_role','primary') or 'primary')=='primary' and not getattr(a,'below_detection',False)]; unique={(a.value_num,a.unit,a.lab_name,a.certificate_ref,a.method) for a in valid}; latest=valid[0] if len(unique)==1 and valid else None; e,n=xy(x.lat,x.lon)
  samples.append({'sample_id':x.sample_id,'hole_id':x.sample_id,'kind':x.sample_type,'lat':x.lat,'lon':x.lon,'e':e,'n':n,'depth':None,'elevation_m':x.elevation_m,'gps_accuracy_m':x.gps_accuracy_m,'rock':x.lithology or '', 'description':x.description or '', 'grade':latest.value_num if latest else None,'assay_count':len(aa),'assay_unit':latest.unit if latest else None,'assay_status':'no_assay' if not aa else 'qa_control_only' if not primary_assays else 'below_detection' if all(getattr(a,'below_detection',False) for a in primary_assays) else 'single_valid' if latest else 'conflicting_or_multiple_assays'})
 collars=[]
 for c in C:
  e,n=xy(c.lat,c.lon); collars.append({**_d(c),'e':e,'n':n})
 raw={'crs':epsg,'collars':collars,'surveys':[_d(s) for s in S],'intervals':[_d(i) for i in I], 'orientations':[_d(o) for o in O], 'samples':samples,'assays':[_d(a) for a in A],'qa_checks':qa_checks}
 h=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
 return {**raw,'project_id':pid,'input_hash':h}
