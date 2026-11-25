"""Build a CRS-explicit, provenance-hashed dataset for processing engines."""
import hashlib,json
from .models import Collar,Survey,Interval,Orientation,Sample,Assay,QAWaiver
from . import geo
def _d(o): return {c.name:getattr(o,c.name) for c in o.__table__.columns if c.name not in ('id','record_uuid','project_id')}

def _batch(value):
 return value.strip().upper() if value and value.strip() else None

def _waives(waivers,control_batch,sample_batches,sample_without_batch):
 return any(
  waiver.batch_id is None
  or (
   not sample_without_batch
   and waiver.batch_id==control_batch
   and control_batch in sample_batches
  )
  for waiver in waivers
 )

def build(db,project):
 pid=project.id; q=lambda M: db.query(M).filter_by(project_id=pid).order_by(M.id).all()
 C,S,I,O,SM,A=q(Collar),q(Survey),q(Interval),q(Orientation),q(Sample),q(Assay)
 all_waivers=q(QAWaiver)
 active_waivers=[w for w in all_waivers if w.revoked_at is None]
 coords=[(x.lon,x.lat) for x in C]+[(x.lon,x.lat) for x in SM]
 epsg=None
 if coords:
  epsg=f"EPSG:{geo.projected_epsg(sum(x for x,y in coords)/len(coords),sum(y for x,y in coords)/len(coords),project.projected_crs)}"
 def xy(lat,lon): return geo.to_projected(lat,lon,epsg)[:2]
 assays_by={}
 for a in A: assays_by.setdefault(a.sample_id,[]).append(a)
 qa_checks=[]
 for a in A:
  role=a.qa_role or 'primary'
  if role=='primary': continue
  status='not_assessed'; detail=''
  if role=='blank':
   limit=a.detection_limit if a.detection_limit is not None else 0.0
   status='pass' if a.value_num<=limit else 'fail'; detail=f'blank={a.value_num}, limit={limit}'
  elif role=='standard':
   if a.certified_value and a.certified_value>0:
    dev=abs(a.value_num-a.certified_value)/a.certified_value*100
    status='pass' if dev<=a.tolerance_pct else 'fail'; detail=f'deviation_pct={dev:.3f}'
  elif role=='duplicate':
   refs=[x for x in A if x.sample_id==a.duplicate_of_sample_id and (x.qa_role or 'primary')=='primary' and x.unit==a.unit]
   distinct={(x.value_num,x.unit,x.lab_name,x.certificate_ref,x.method) for x in refs}
   if len(distinct)==1 and refs:
    ref=refs[-1]; denom=(abs(a.value_num)+abs(ref.value_num))/2
    rpd=abs(a.value_num-ref.value_num)/denom*100 if denom else 0.0
    status='pass' if rpd<=a.tolerance_pct else 'fail'; detail=f'RPD_pct={rpd:.3f}'
   elif len(distinct)>1: status='not_assessed'; detail='Primary assays nyingi zinapingana; duplicate haiwezi kulinganishwa'
   else: status='pending'; detail='primary assay haijafika'
  qa_checks.append({'sample_id':a.sample_id,'role':role,'batch_id':_batch(a.batch_id),'status':status,'detail':detail,'record_uuid':a.record_uuid})
 samples=[]
 below_detection_imputed_count=0
 qa_blocked_sample_count=0
 qa_waived_sample_count=0
 for x in SM:
  aa=assays_by.get(x.sample_id,[])
  primary=[a for a in aa if (a.qa_role or 'primary')=='primary']
  valid=[a for a in primary if a.unit=='g/t' and not a.below_detection]
  unique={(a.value_num,a.unit,a.lab_name,a.certificate_ref,a.method) for a in valid}
  latest=valid[-1] if len(unique)==1 and valid and not any(a.below_detection for a in primary) else None
  grade=latest.value_num if latest else None
  grade_basis='reported' if latest else None
  assay_status='no_assay' if not aa else 'qa_control_only' if not primary else 'conflicting_or_multiple_assays'
  if latest:
   assay_status='single_valid'
  elif primary and all(a.below_detection for a in primary):
   if all(a.unit=='g/t' and a.detection_limit is not None for a in primary):
    limits={float(a.detection_limit) for a in primary}
    if len(limits)==1:
     grade=next(iter(limits))/2
     grade_basis='below_detection_half_dl'
     assay_status='below_detection'
     below_detection_imputed_count+=1
    else:
     assay_status='conflicting_detection_limits'
   else:
    assay_status='below_detection_unusable'
  sample_batches={_batch(a.batch_id) for a in primary if _batch(a.batch_id)}
  sample_without_batch=not sample_batches or any(_batch(a.batch_id) is None for a in primary)
  blocking=[]
  for check in qa_checks:
   if check['status']=='pass':
    continue
   control_batch=check['batch_id']
   applies=control_batch is None or sample_without_batch or control_batch in sample_batches
   if applies:
    blocking.append(check)
  unwaived=[check for check in blocking if not _waives(active_waivers,check['batch_id'],sample_batches,sample_without_batch)]
  if unwaived:
   qa_status='blocked'
   qa_blocked_sample_count+=1
   grade=None
   grade_basis=None
  elif blocking:
   qa_status='waived'
   qa_waived_sample_count+=1
  else:
   qa_status='pass' if qa_checks else 'not_assessed'
  e,n=xy(x.lat,x.lon)
  samples.append({
   'sample_id':x.sample_id,'record_uuid':x.record_uuid,'hole_id':x.sample_id,'kind':x.sample_type,
   'lat':x.lat,'lon':x.lon,'e':e,'n':n,'depth':None,'elevation_m':x.elevation_m,
   'gps_accuracy_m':x.gps_accuracy_m,'rock':x.lithology or '', 'description':x.description or '',
   'grade':grade,'grade_basis':grade_basis,'assay_count':len(aa),
   'primary_assay_count':len(primary),'below_detection_count':sum(a.below_detection for a in primary),
   'assay_unit':latest.unit if latest else 'g/t' if grade_basis=='below_detection_half_dl' else None,
   'assay_status':assay_status,'qa_status':qa_status,
   'qa_batch_ids':sorted(sample_batches),
  })
 collars=[]
 for c in C:
  e,n=xy(c.lat,c.lon); collars.append({**_d(c),'e':e,'n':n})
 waiver_rows=[{
  'id':w.id,'batch_id':w.batch_id,'reason':w.reason,'created_by':w.created_by,
  'created_by_username':w.created_by_username,'created_at':w.created_at,
  'revoked_at':w.revoked_at,'revoked_by':w.revoked_by,
 } for w in all_waivers]
 processing_warnings=[]
 if below_detection_imputed_count:
  processing_warnings.append(f'{below_detection_imputed_count} sampuli zenye assays zote chini ya detection limit zimechangiwa kwa DL/2 (sera ya awali; thibitishwa na mwanajiolojia).')
 if qa_blocked_sample_count:
  processing_warnings.append(f'QA/QC imezuia grades za sampuli {qa_blocked_sample_count} kutokana na batch/control zinazohusika.')
 if qa_waived_sample_count:
  processing_warnings.append(f'Waiver ya QA/QC imeruhusu matumizi ya sampuli {qa_waived_sample_count}; angalia sababu na mkaguzi kwenye rekodi za mradi.')
 qa_waivers=[{
  'id':w.id,'batch_id':w.batch_id,'reason':w.reason,'created_by_username':w.created_by_username,
  'created_at':w.created_at,
 } for w in active_waivers]
 raw={
  'crs':epsg,'collars':collars,'surveys':[_d(s) for s in S],'intervals':[_d(i) for i in I],
  'orientations':[_d(o) for o in O],'samples':samples,'assays':[_d(a) for a in A],
  'qa_checks':qa_checks,'qa_waivers':waiver_rows,
 }
 h=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
 counts={
  'sample_count':len(samples),'below_detection_imputed_count':below_detection_imputed_count,
  'qa_blocked_sample_count':qa_blocked_sample_count,'qa_waived_sample_count':qa_waived_sample_count,
  'qa_blocked_sample_counts_by_type':{
   kind:sum(1 for sample in samples if sample['kind']==kind and sample['qa_status']=='blocked')
   for kind in sorted({sample['kind'] for sample in samples})
  },
 }
 return {
  **raw,'project_id':pid,'input_hash':h,'processing_warnings':processing_warnings,
  'processing_counts':counts,'active_qa_waivers':qa_waivers,
 }
