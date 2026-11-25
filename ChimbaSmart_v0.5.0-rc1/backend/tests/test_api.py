import hashlib, json, os, pytest, secrets, uuid
from datetime import datetime,timedelta,timezone
from conftest import *
from app.models import PasswordResetToken
from app.security import create_token


@pytest.fixture(autouse=True)
def redis_test_isolation():
    if os.getenv('REDIS_URL'):
        import redis
        client=redis.Redis.from_url(os.environ['REDIS_URL'],decode_responses=True)
        client.flushdb()
    yield
    if os.getenv('REDIS_URL'):
        import redis
        client=redis.Redis.from_url(os.environ['REDIS_URL'],decode_responses=True)
        client.flushdb()
def push(c,h,*r): return c.post('/sync/push',json={'records':list(r)},headers=h)
def st(res): return [a['status'] for a in res.json()['accepted']]
def test_login_and_throttle(client):
    n=mkuser(); assert client.post('/auth/login',json={'username':n,'password':PW}).status_code==200
    for _ in range(5): assert client.post('/auth/login',json={'username':n,'password':'x'}).status_code==401
    assert client.post('/auth/login',json={'username':n,'password':PW}).status_code==429
def test_admin_only_user_creation(client):
    assert client.post('/admin/users',json={'username':'abc','password':'12345678'},headers=hdr(client,mkuser())).status_code==403
    r=client.post('/admin/users',json={'username':'Nyuma'+mkuser()[:4],'password':'12345678'},headers=hdr(client,mkuser('admin'))); assert r.status_code==201
def test_push_duplicate_conflict(ctx,client):
    h,p=ctx; c=rec(p,'collar',collar('s1',0)); a=rec(p,'interval',assay('S1',2.0))
    assert sorted(st(push(client,h,a,c)))==['accepted','accepted']   # a kabla ya c: seva inapanga
    assert st(push(client,h,c))==['duplicate']
    c['payload']['depth_m']=4.0; assert st(push(client,h,c))==['conflict']
def test_server_ignores_client_hash(ctx,client):
    h,p=ctx; r=rec(p,'collar',collar('H1',0)); r['content_hash']='f'*64; assert st(push(client,h,r))==['accepted']
def test_qa_rules(ctx,client):
    h,p=ctx; push(client,h,rec(p,'collar',collar('Q1',0)))
    too_deep=push(client,h,rec(p,'interval',assay('Q1',1,0,5))).json()['accepted'][0]; assert too_deep['status']=='invalid' and not too_deep['retry']
    orphan=push(client,h,rec(p,'interval',assay('NOPE',1))).json()['accepted'][0]; assert orphan['status']=='invalid' and orphan['retry']
    assert st(push(client,h,rec(p,'collar',collar('q1',1))))==['invalid']            # namba ya shimo marudio
    push(client,h,rec(p,'interval',assay('Q1',1,0,2))); assert st(push(client,h,rec(p,'interval',assay('Q1',2,1,3))))==['invalid']  # kugongana
    assert st(push(client,h,rec(p,'interval',assay('Q1',-1,2,3))))==['invalid']      # assay hasi
def test_authorization(ctx,client):
    h,p=ctx; o=hdr(client,mkuser())
    assert push(client,o,rec(p,'collar',collar('X',0))).status_code==403
    assert client.get(f'/sync/pull?project_id={p}',headers=o).status_code==403
    assert client.get(f'/projects/{p}/analysis',headers=o).status_code==403
    assert client.get('/sync/pull?project_id='+p).status_code==401
def _fill(c,h,p):
    rs=[]
    for i in range(6):
        rs += [rec(p,'collar',collar(f'T{i}',i)),rec(p,'interval',assay(f'T{i}',float(i))),rec(p,'sample',{'sample_id':f'S{i}','sample_type':'rock_chip','lat':-3.0+[0,.001,-.001,-.001,.001,0][i],'lon':32.1+i*0.001,'gps_accuracy_m':4,'location_method':'phone_gps'}),rec(p,'assay',{'sample_id':f'S{i}','value_num':float(i),'unit':'g/t'})]
    rs.append(rec(p,'orientation',{'lat':-3.0,'lon':32.1,'strike_deg':10,'dip_deg':40})); rs.append(rec(p,'orientation',{'lat':-3.0,'lon':32.1,'strike_deg':20,'dip_deg':50}))
    assert set(st(push(c,h,*rs)))=={'accepted'}
def test_analysis(ctx,client):
    h,p=ctx; _fill(client,h,p); r=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert r['crs'] in('EPSG:32736','EPSG:32735') and r['trend']['ok'] and abs(r['trend']['bearing']-90)<15
    assert abs(r['plane']['strike']-15)<3 and abs(r['plane']['dip']-45)<3
    assert client.get(f'/projects/{p}/report.pdf',headers=h).status_code==200
def test_jobs(ctx,client):
    h,p=ctx; _fill(client,h,p)
    j=client.post('/jobs',json={'project_id':p,'engine':'trend2d'},headers=h).json()
    r=client.get('/jobs/'+j['id'],headers=h).json(); assert r['status']=='done' and r['input_hash'] and r['result']['trend']['ok']
    g=client.post('/jobs',json={'project_id':p,'engine':'gempy'},headers=h).json()
    assert client.get('/jobs/'+g['id'],headers=h).json()['status']=='rejected'      # adapter bado
    assert client.post('/jobs',json={'project_id':p,'engine':'nope'},headers=h).status_code==400


def test_surface_sample_is_separate_and_assay_can_arrive_later(ctx,client):
    h,p=ctx
    sample=rec(p,'sample',{'sample_id':'ROCK-01','sample_type':'rock_chip','lat':-3.1,'lon':32.2,'gps_accuracy_m':3,'lithology':'Quartz','location_method':'phone_gps'})
    assert st(push(client,h,sample))==['accepted']
    a=rec(p,'assay',{'sample_id':'ROCK-01','value_num':4.2,'unit':'g/t','lab_name':'Lab A','certificate_ref':'CERT-1'})
    assert st(push(client,h,a))==['accepted']
    d=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert d['samples'][0]['sample_id']=='ROCK-01' and d['samples'][0]['grade']==4.2
    assert d['samples'][0]['depth'] is None

def test_assay_waits_for_sample(ctx,client):
    h,p=ctx; a=rec(p,'assay',{'sample_id':'LATER','value_num':1.2,'unit':'g/t'})
    ack=push(client,h,a).json()['accepted'][0]
    assert ack['status']=='invalid' and ack['retry'] is True

def test_pull_returns_cursor_and_sample_records(ctx,client):
    h,p=ctx; s=rec(p,'sample',{'sample_id':'PULL-1','sample_type':'soil','lat':-3.1,'lon':32.2})
    assert st(push(client,h,s))==['accepted']
    r=client.get(f'/sync/pull?project_id={p}&cursor=0',headers=h).json()
    assert any(x['record_type']=='sample' for x in r['records']) and r['next_cursor'] is not None

def test_idw_engine_returns_grid(ctx,client):
    from app.engines import ENGINES
    from app.db import SessionLocal
    from app.models import Project
    h,p=ctx; _fill(client,h,p); db=SessionLocal()
    try:
        ds=__import__('app.dataset',fromlist=['build']).build(db,db.get(Project,p))
        e=ENGINES['idw']; assert e.validate(ds)==[]
        out=e.run(ds,{'grid_size':5,'power':2})
        assert out['method']=='IDW' and len(out['values'])==5 and len(out['values'][0])==5 and out['input_hash']==ds['input_hash']
    finally: db.close()

def test_attachment_requires_valid_sample_and_type(ctx,client):
    h,p=ctx
    r=client.post('/attachments',data={'project_id':p,'sample_id':'MISSING','sample_record_uuid':str(uuid.uuid4())},files={'file':('x.txt',b'abc','text/plain')},headers=h)
    assert r.status_code==404
    s=rec(p,'sample',{'sample_id':'PHOTO-1','sample_type':'rock_chip','lat':-3.1,'lon':32.2})
    assert st(push(client,h,s))==['accepted']
    bad=client.post('/attachments',data={'project_id':p,'sample_id':'PHOTO-1','sample_record_uuid':s['record_uuid']},files={'file':('x.txt',b'abc','text/plain')},headers=h)
    assert bad.status_code==415


def test_read_only_project_member_cannot_upload_attachment(ctx,client):
    h,p=ctx
    reader=mkuser()
    assert client.post(f'/projects/{p}/members',json={'username':reader,'role':'read_only'},headers=h).status_code==201
    response=client.post(
        '/attachments',
        data={'project_id':p,'sample_id':'PHOTO-1','sample_record_uuid':str(uuid.uuid4())},
        files={'file':('photo.png',b'not-an-image','image/png')},
        headers=hdr(client,reader),
    )
    assert response.status_code==403


def test_downhole_composite_is_length_weighted(ctx,client):
    from app.engines import ENGINES
    from app.db import SessionLocal
    from app.models import Project
    h,p=ctx; push(client,h,rec(p,'collar',collar('COMP-1',0)),rec(p,'interval',assay('COMP-1',2.0,0,1)),rec(p,'interval',assay('COMP-1',4.0,1,2)))
    db=SessionLocal()
    try:
        ds=__import__('app.dataset',fromlist=['build']).build(db,db.get(Project,p))
        e=ENGINES['downhole_composite']; assert e.validate(ds)==[]
        out=e.run(ds,{'composite_length_m':2.0})
        assert len(out['composites'])==1 and out['composites'][0]['grade']==3.0 and out['composites'][0]['coverage']==1.0
    finally: db.close()


def test_multiple_primary_assays_are_not_silently_selected(ctx,client):
    h,p=ctx
    sample=rec(p,'sample',{'sample_id':'MULTI-1','sample_type':'rock_chip','lat':-3.1,'lon':32.2})
    assert st(push(client,h,sample))==['accepted']
    a1=rec(p,'assay',{'sample_id':'MULTI-1','value_num':1.2,'unit':'g/t','certificate_ref':'A'})
    a2=rec(p,'assay',{'sample_id':'MULTI-1','value_num':9.8,'unit':'g/t','certificate_ref':'B'})
    assert set(st(push(client,h,a1,a2)))=={'accepted'}
    d=client.get(f'/projects/{p}/analysis',headers=h).json()
    row=next(x for x in d['samples'] if x['sample_id']=='MULTI-1')
    assert row['grade'] is None and row['assay_status']=='conflicting_or_multiple_assays'
    listed=client.get(f'/projects/{p}/samples',headers=h).json()['samples'][0]
    assert listed['grade'] is None and listed['assay_status']=='conflicting_or_multiple_assays'

def test_assay_qaqc_roles(ctx,client):
    h,p=ctx
    samples=[rec(p,'sample',{'sample_id':sid,'sample_type':'rock_chip','lat':-3.1,'lon':32.2+i*.001}) for i,sid in enumerate(['PRIMARY-1','BLANK-1','STD-1'])]
    assert set(st(push(client,h,*samples)))=={'accepted'}
    assays=[
      rec(p,'assay',{'sample_id':'PRIMARY-1','value_num':2.0,'unit':'g/t','qa_role':'primary','batch_id':'B1'}),
      rec(p,'assay',{'sample_id':'BLANK-1','value_num':0.01,'unit':'g/t','qa_role':'blank','detection_limit':0.02,'batch_id':'B1'}),
      rec(p,'assay',{'sample_id':'STD-1','value_num':9.7,'unit':'g/t','qa_role':'standard','certified_value':10.0,'tolerance_pct':5,'batch_id':'B1'}),
    ]
    assert set(st(push(client,h,*assays)))=={'accepted'}
    d=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert len(d['qa_checks'])==2 and all(x['status']=='pass' for x in d['qa_checks'])

def test_attachment_success_and_duplicate_is_idempotent(ctx,client):
    from PIL import Image
    import io
    from pathlib import Path
    h,p=ctx
    s=rec(p,'sample',{'sample_id':'PHOTO-OK','sample_type':'rock_chip','lat':-3.1,'lon':32.2})
    assert st(push(client,h,s))==['accepted']
    b=io.BytesIO(); Image.new('RGB',(2,2),(255,0,0)).save(b,format='PNG'); payload=b.getvalue()
    attachment_dir=Path(os.environ['ATTACHMENTS_DIR'])
    before=set(attachment_dir.iterdir()) if attachment_dir.exists() else set()
    args={'data':{'project_id':p,'sample_id':'PHOTO-OK','sample_record_uuid':s['record_uuid']},'files':{'file':('sample.png',payload,'image/png')},'headers':h}
    first=client.post('/attachments',**args); assert first.status_code==201
    assert set(attachment_dir.iterdir())-before
    second=client.post('/attachments',**args); assert second.status_code==201 and second.json().get('duplicate') is True


def test_analysis_separates_sample_types_and_requires_choice_on_tie(ctx,client):
    h,p=ctx
    records=[]
    for kind,prefix,offset in [('rock_chip','R',0),('soil','S',1)]:
        for i in range(4):
            records.append(rec(p,'sample',{'sample_id':f'{prefix}{i}','sample_type':kind,'lat':-3.0+(i//2)*0.001,'lon':32.1+(i%2)*0.001+offset*0.01}))
            records.append(rec(p,'assay',{'sample_id':f'{prefix}{i}','value_num':float(i+1),'unit':'g/t'}))
    assert set(st(push(client,h,*records)))=={'accepted'}
    all_data=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert not all_data['trend']['ok'] and 'chagua aina' in all_data['trend']['msg'].lower()
    selected=client.get(f'/projects/{p}/analysis?sample_type=soil',headers=h).json()
    assert selected['trend']['sample_type']=='soil'
    assert all(x['kind']=='soil' for x in selected['samples'])


def test_failed_qaqc_blocks_grade_engines(ctx,client):
    from app.db import SessionLocal
    from app.models import Project
    from app import dataset as dsmod
    from app.engines import ENGINES
    h,p=ctx
    items=[rec(p,'sample',{'sample_id':sid,'sample_type':'rock_chip','lat':-3.0+(i//2)*.001,'lon':32.1+(i%2)*.001}) for i,sid in enumerate(['P1','P2','P3','P4','B1'])]
    assert set(st(push(client,h,*items)))=={'accepted'}
    assays=[rec(p,'assay',{'sample_id':f'P{i}','value_num':i+1,'unit':'g/t'}) for i in range(1,5)]
    assays.append(rec(p,'assay',{'sample_id':'B1','value_num':1.0,'unit':'g/t','qa_role':'blank','detection_limit':0.01,'batch_id':'BAD'}))
    assert set(st(push(client,h,*assays)))=={'accepted'}
    db=SessionLocal()
    try:
        data=dsmod.build(db,db.get(Project,p))
        assert ENGINES['trend2d'].validate(data)
        assert ENGINES['idw'].validate(data)
    finally: db.close()


def test_assay_below_detection_requires_limit_and_is_not_grade(ctx,client):
    h,p=ctx
    sample=rec(p,'sample',{'sample_id':'BDL','sample_type':'soil','lat':-3.1,'lon':32.2})
    assert st(push(client,h,sample))==['accepted']
    invalid=rec(p,'assay',{'sample_id':'BDL','value_num':0.01,'unit':'g/t','below_detection':True})
    assert push(client,h,invalid).json()['accepted'][0]['status']=='invalid'
    valid=rec(p,'assay',{'sample_id':'BDL','value_num':0.01,'unit':'g/t','below_detection':True,'detection_limit':0.02})
    assert st(push(client,h,valid))==['accepted']
    d=client.get(f'/projects/{p}/analysis?sample_type=soil',headers=h).json()
    assert d['samples'][0]['grade']==0.01
    assert d['samples'][0]['grade_basis']=='below_detection_half_dl'
    assert d['processing_counts']['below_detection_imputed_count']==1
    assert any('DL/2' in warning for warning in d['warnings'])


def test_sample_list_shows_latest_assay_attachments_and_sync_fields(ctx,client):
    from PIL import Image
    import io
    h,p=ctx
    sample=rec(p,'sample',{'sample_id':'LIST-1','sample_type':'soil','lat':-3.1,'lon':32.2})
    assert st(push(client,h,sample))==['accepted']
    first=rec(p,'assay',{'sample_id':'LIST-1','value_num':1.2,'unit':'g/t','certificate_ref':'CERT-1'})
    latest=rec(p,'assay',{'sample_id':'LIST-1','value_num':2.4,'unit':'g/t','certificate_ref':'CERT-2'})
    assert set(st(push(client,h,first,latest)))=={'accepted'}
    image=io.BytesIO()
    Image.new('RGB',(2,2),(255,0,0)).save(image,format='PNG')
    uploaded=client.post(
        '/attachments',
        data={'project_id':p,'sample_id':'LIST-1','sample_record_uuid':sample['record_uuid']},
        files={'file':('list.png',image.getvalue(),'image/png')},headers=h,
    )
    assert uploaded.status_code==201
    response=client.get(f'/projects/{p}/samples',headers=h)
    assert response.status_code==200
    row=response.json()['samples'][0]
    assert row['sample_id']=='LIST-1'
    assert row['latest_assay']['certificate_ref']=='CERT-2'
    assert row['attachment_count']==1
    assert row['sync_status']=='synced' and row['server_version']==1
    assert row['qa_status']=='not_assessed'


def test_sample_list_and_qa_waivers_are_project_isolated(ctx,client):
    h,p=ctx
    other_user=mkuser()
    other_headers=hdr(client,other_user)
    other_project=client.post('/projects',json={'name':'Other project'},headers=other_headers).json()['id']
    assert client.get(f'/projects/{p}/samples',headers=other_headers).status_code==403
    assert client.post(
        f'/projects/{other_project}/qa/waivers',
        json={'batch_id':'B1','reason':'Reviewed and approved'},headers=h,
    ).status_code==403


def test_qaqc_is_scoped_to_batch_and_warnings_reach_jobs(ctx,client):
    h,p=ctx
    records=[]
    for i in range(4):
        sample_id=f'GOOD-{i}'
        records.extend([
            rec(p,'sample',{'sample_id':sample_id,'sample_type':'rock_chip','lat':-3.0+i*.001,'lon':32.1+i*.001}),
            rec(p,'assay',{'sample_id':sample_id,'value_num':float(i+1),'unit':'g/t','batch_id':'GOOD'}),
        ])
    records.extend([
        rec(p,'sample',{'sample_id':'BAD-1','sample_type':'rock_chip','lat':-3.01,'lon':32.11}),
        rec(p,'assay',{'sample_id':'BAD-1','value_num':5.0,'unit':'g/t','batch_id':'BAD'}),
        rec(p,'sample',{'sample_id':'BLANK-1','sample_type':'rock_chip','lat':-3.02,'lon':32.12}),
        rec(p,'assay',{'sample_id':'BLANK-1','value_num':1.0,'unit':'g/t','qa_role':'blank','detection_limit':0.01,'batch_id':'BAD'}),
    ])
    assert set(st(push(client,h,*records)))=={'accepted'}
    analysis=client.get(f'/projects/{p}/analysis',headers=h).json()
    grades={sample['sample_id']:sample['grade'] for sample in analysis['samples']}
    assert grades['GOOD-0']==1.0 and grades['BAD-1'] is None
    job=client.post('/jobs',json={'project_id':p,'engine':'trend2d','params':{'sample_type':'rock_chip'}},headers=h).json()
    result=client.get(f"/jobs/{job['id']}",headers=h).json()
    assert result['status']=='done'
    assert result['result']['processing_counts']['qa_blocked_sample_count']>0
    assert any('QA/QC imezuia' in warning for warning in result['warnings'])


def test_qa_waiver_creation_revocation_and_hash_provenance(ctx,client):
    from app.models import QAWaiver
    h,p=ctx
    records=[]
    for i in range(4):
        sample_id=f'WAIVE-{i}'
        records.extend([
            rec(p,'sample',{'sample_id':sample_id,'sample_type':'soil','lat':-3.0+i*.001,'lon':32.1+i*.001}),
            rec(p,'assay',{'sample_id':sample_id,'value_num':float(i+1),'unit':'g/t','batch_id':'B-1'}),
        ])
    records.extend([
        rec(p,'sample',{'sample_id':'WAIVE-BLANK','sample_type':'soil','lat':-3.01,'lon':32.11}),
        rec(p,'assay',{'sample_id':'WAIVE-BLANK','value_num':1.0,'unit':'g/t','qa_role':'blank','detection_limit':0.01,'batch_id':'B-1'}),
    ])
    assert set(st(push(client,h,*records)))=={'accepted'}
    before=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert next(row for row in before['samples'] if row['sample_id']=='WAIVE-0')['grade'] is None
    assert client.post(
        f'/projects/{p}/qa/waivers',json={'batch_id':'B-1','reason':'   too short   '},headers=h
    ).status_code==422
    reviewer=mkuser()
    assert client.post(f'/projects/{p}/members',json={'username':reviewer,'role':'geologist'},headers=h).status_code==201
    assert client.post(
        f'/projects/{p}/qa/waivers',json={'batch_id':'B-1','reason':'Reviewed batch evidence'},headers=hdr(client,reviewer)
    ).status_code==403
    created=client.post(
        f'/projects/{p}/qa/waivers',json={'batch_id':' b-1 ','reason':'Reviewed batch evidence'},headers=h
    )
    assert created.status_code==201
    waiver=created.json()
    assert waiver['batch_id']=='B-1' and waiver['created_by_username']
    waived=client.get(f'/projects/{p}/analysis',headers=h).json()
    waived_sample=next(row for row in waived['samples'] if row['sample_id']=='WAIVE-0')
    waived_control=next(row for row in waived['samples'] if row['sample_id']=='WAIVE-BLANK')
    assert waived['input_hash']!=before['input_hash']
    assert waived_sample['grade']==1.0 and waived_sample['qa_status']=='waived'
    assert waived_control['grade'] is None and waived_control['qa_status']=='blocked'
    assert any('Waiver ya QA/QC' in warning for warning in waived['warnings'])
    revoked=client.delete(f"/projects/{p}/qa/waivers/{waiver['id']}",headers=h)
    assert revoked.status_code==200
    restored=client.get(f'/projects/{p}/analysis',headers=h).json()
    assert restored['input_hash'] not in {before['input_hash'],waived['input_hash']}
    assert next(row for row in restored['samples'] if row['sample_id']=='WAIVE-0')['grade'] is None
    db=SessionLocal()
    try:
        stored=db.get(QAWaiver,waiver['id'])
        assert stored and stored.revoked_at and stored.revoked_by
        assert stored.created_by_username==db.get(User,stored.created_by).username
    finally:
        db.close()


def test_below_detection_conflicting_limits_are_not_imputed(ctx,client):
    h,p=ctx
    sample=rec(p,'sample',{'sample_id':'BDL-CONFLICT','sample_type':'soil','lat':-3.1,'lon':32.2})
    assays=[
        rec(p,'assay',{'sample_id':'BDL-CONFLICT','value_num':0.01,'unit':'g/t','below_detection':True,'detection_limit':0.02}),
        rec(p,'assay',{'sample_id':'BDL-CONFLICT','value_num':0.02,'unit':'g/t','below_detection':True,'detection_limit':0.04}),
    ]
    assert st(push(client,h,sample,*assays))==['accepted','accepted','accepted']
    result=client.get(f'/projects/{p}/analysis?sample_type=soil',headers=h).json()
    row=result['samples'][0]
    assert row['grade'] is None and row['assay_status']=='conflicting_detection_limits'


def test_one_username_ip_lock_does_not_lock_other_user(client):
    user_a=mkuser(); user_b=mkuser()
    for _ in range(5):
        assert client.post('/auth/login',json={'username':user_a,'password':'wrong-password'}).status_code==401
    assert client.post('/auth/login',json={'username':user_a,'password':PW}).status_code==429
    # Same test-client IP, different username: must remain able to sign in.
    assert client.post('/auth/login',json={'username':user_b,'password':PW}).status_code==200


def test_refresh_rotation_and_reuse(client):
    n=mkuser()
    login=client.post('/auth/login',json={'username':n,'password':PW})
    assert login.status_code==200
    old_access=login.json()['access_token']
    refresh=login.json()['refresh_token']
    assert refresh
    first=client.post('/auth/refresh',json={'refresh_token':refresh})
    assert first.status_code==200
    replacement=first.json()['refresh_token']
    assert replacement and replacement!=refresh
    assert client.post('/auth/refresh',json={'refresh_token':refresh}).status_code==401
    assert client.post('/auth/refresh',json={'refresh_token':replacement}).status_code==200
    assert client.get('/projects',headers={'Authorization':'Bearer '+old_access}).status_code==401


def test_password_reset_revokes_refresh_sessions(client):
    n=mkuser()
    login=client.post('/auth/login',json={'username':n,'password':PW})
    refresh=login.json()['refresh_token']
    raw=secrets.token_urlsafe(48)
    db=SessionLocal()
    try:
        db.add(PasswordResetToken(
            id=str(uuid.uuid4()),user_id=db.query(User).filter_by(username=n).first().id,
            token_hash=hashlib.sha256(raw.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc)+timedelta(minutes=30),
        ))
        db.commit()
    finally:
        db.close()
    result=client.post('/auth/password-reset/confirm',json={'token':raw,'password':'New-Secure-Password-123'})
    assert result.status_code==200
    assert client.get('/projects',headers={'Authorization':'Bearer '+login.json()['access_token']}).status_code==401
    assert client.post('/auth/refresh',json={'refresh_token':refresh}).status_code==401
    assert client.post('/auth/login',json={'username':n,'password':'New-Secure-Password-123'}).status_code==200

def test_logout_revokes_only_current_session(client):
    n=mkuser()
    first=client.post('/auth/login',json={'username':n,'password':PW}).json()
    second=client.post('/auth/login',json={'username':n,'password':PW}).json()
    first_headers={'Authorization':'Bearer '+first['access_token']}
    second_headers={'Authorization':'Bearer '+second['access_token']}
    assert client.get('/projects',headers=first_headers).status_code==200
    assert client.get('/projects',headers=second_headers).status_code==200
    assert client.post('/auth/logout',json={},headers=first_headers).status_code==200
    assert client.get('/projects',headers=first_headers).status_code==401
    assert client.post('/auth/refresh',json={'refresh_token':first['refresh_token']}).status_code==401
    assert client.get('/projects',headers=second_headers).status_code==200

def test_logout_invalidates_legacy_access_tokens(client):
    n=mkuser()
    login=client.post('/auth/login',json={'username':n,'password':PW}).json()
    db=SessionLocal()
    try:
        user=db.query(User).filter_by(username=n).first()
        token=create_token(user.id)
    finally:
        db.close()
    headers={'Authorization':'Bearer '+token}
    assert client.post('/auth/logout',json={},headers=headers).status_code==200
    assert client.get('/projects',headers=headers).status_code==401
    assert client.post('/auth/refresh',json={'refresh_token':login['refresh_token']}).status_code==401

def test_password_reset_request_does_not_revoke_sessions(client):
    n=mkuser()
    login=client.post('/auth/login',json={'username':n,'password':PW}).json()
    request=client.post('/auth/password-reset/request',json={'username':n})
    assert request.status_code==200
    assert client.post('/auth/refresh',json={'refresh_token':login['refresh_token']}).status_code==200


def test_configurable_project_role_permissions(ctx,client):
    h,p=ctx
    technician=mkuser()
    assert client.post(f'/projects/{p}/members',json={'username':technician,'role':'field_technician'},headers=h).status_code==201
    technician_headers=hdr(client,technician)
    assert client.post('/jobs',json={'project_id':p,'engine':'trend2d'},headers=technician_headers).status_code==403


@pytest.mark.skipif(not os.getenv('REDIS_URL'),reason='REDIS_URL haijawekwa')
def test_redis_rate_limit_is_available(client):
    import redis
    r=redis.Redis.from_url(os.environ['REDIS_URL'],decode_responses=True)
    r.ping()
    r.incr('test:rate-limit')


def test_conflict_resolution_keep_server(ctx,client):
    h,p=ctx
    first=rec(p,'collar',collar('CONFLICT-1',0))
    assert st(push(client,h,first))==['accepted']
    changed=dict(first); changed['payload']=collar('CONFLICT-1',1)
    ack=push(client,h,changed).json()['accepted'][0]
    assert ack['status']=='conflict'
    listing=client.get(f'/projects/{p}/conflicts',headers=h)
    assert listing.status_code==200 and listing.json()[0]['record_uuid']==first['record_uuid']
    resolved=client.post(
        f"/projects/{p}/conflicts/{listing.json()[0]['id']}/resolve",
        json={'resolution':'keep_server'},headers=h)
    assert resolved.status_code==200
    assert resolved.json()['resolution']=='keep_server'
