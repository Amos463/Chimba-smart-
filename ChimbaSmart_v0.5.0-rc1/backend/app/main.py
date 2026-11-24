import hashlib,json,uuid,os,time,collections,mimetypes,secrets,io
from datetime import datetime,timedelta,timezone
from fastapi import FastAPI,Depends,HTTPException,BackgroundTasks,Response,UploadFile,File,Form,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import jwt
from . import config,dataset,typed,report
from .engines import ENGINES,DISCLAIMER,quick
from .db import Base,engine,get_db,SessionLocal
from .models import User,Project,ProjectMember,Record,SyncConflict,Job,Attachment,Sample,RefreshSession,PasswordResetToken,AuditEvent,utcnow
from .schemas import *
from .security import verify_password,hash_password,create_token,decode_token
app=FastAPI(title='ChimbaSmart API',version='0.5.0-rc1',description='Offline-first geological field data API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'],
    allow_headers=['Authorization','Content-Type','X-Request-ID'],
)
bearer=HTTPBearer(auto_error=False)
if config.AUTO_CREATE_TABLES: Base.metadata.create_all(bind=engine)  # prod: tumia alembic
canon=lambda p: json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False)
sha=lambda p: hashlib.sha256(canon(p).encode()).hexdigest()
def current_user(creds:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not creds: raise HTTPException(401,'Ingia kwanza')
    try: uid=decode_token(creds.credentials)['sub']
    except jwt.PyJWTError: raise HTTPException(401,'Kipindi kimeisha, ingia tena')
    u=db.get(User,uid)
    if not u: raise HTTPException(401,'Mtumiaji hajulikani')
    return u
def need_member(db,user,pid,owner=False):
    p=db.get(Project,pid)
    if not p: raise HTTPException(404,'Mradi haupo')
    if user.role=='admin': return p
    m=db.get(ProjectMember,(pid,user.id))
    if not m or (owner and m.role!='owner'): raise HTTPException(403,'Huna ruhusa ya mradi huu')
    return p


def require_permission(db,user,pid,permission):
    p=need_member(db,user,pid)
    if user.role=='admin':
        return p
    m=db.get(ProjectMember,(pid,user.id))
    role=m.role if m else ''
    if permission not in config.PROJECT_ROLE_PERMISSIONS.get(role,set()):
        raise HTTPException(403,'Huna ruhusa ya hatua hii')
    return p


def redis_client():
    if not config.REDIS_URL:
        return None
    try:
        import redis
        return redis.Redis.from_url(config.REDIS_URL,decode_responses=True,socket_connect_timeout=2)
    except Exception:
        return None


def distributed_throttle(key,limit,window_s):
    client=redis_client()
    if client is None:
        return
    try:
        now=int(time.time()); bucket=f'rate:{key}:{now//window_s}'
        count=client.incr(bucket)
        if count==1:
            client.expire(bucket,window_s)
        if count>limit:
            raise HTTPException(429,'Majaribio mengi. Subiri kisha jaribu tena.')
    except HTTPException:
        raise
    except Exception:
        return
FAILS=collections.defaultdict(list)  # kwenye kumbukumbu ya process moja; prod yenye workers nyingi: tumia Redis


def audit(db:Session, request:Request|None, action:str, *, actor_id:str|None=None, project_id:str|None=None,
          resource_type:str|None=None, resource_id:str|None=None, outcome:str='success', details:dict|None=None):
    db.add(AuditEvent(
        actor_id=actor_id, project_id=project_id, action=action, resource_type=resource_type,
        resource_id=resource_id, outcome=outcome,
        ip_address=request.client.host if request and request.client else None,
        request_id=request.headers.get('x-request-id') if request else None,
        details_json=canon(details) if details else None,
    ))


def utc_aware(value:datetime|None)->datetime|None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@app.middleware('http')
async def security_middleware(request:Request, call_next):
    request_id=request.headers.get('x-request-id') or str(uuid.uuid4())
    content_length=request.headers.get('content-length')
    if content_length:
        try:
            if int(content_length)>config.MAX_REQUEST_BYTES:
                raise HTTPException(413,'Request imezidi ukubwa unaoruhusiwa')
        except ValueError:
            raise HTTPException(400,'Content-Length si sahihi')
    response=await call_next(request)
    response.headers['X-Request-ID']=request_id
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Cache-Control']='no-store'
    return response
def throttle(k,limit=None):
    now=time.time(); FAILS[k]=[t for t in FAILS[k] if now-t<config.LOGIN_WINDOW_S]
    if len(FAILS[k])>=(limit or config.LOGIN_MAX_FAILS): raise HTTPException(429,'Majaribio mengi. Subiri dakika 15.')
@app.get('/health')
def health(): return {'status':'ok','time_utc':datetime.now(timezone.utc).isoformat()}
@app.get('/ready')
def readiness(db:Session=Depends(get_db)):
    try:
        db.execute(__import__('sqlalchemy').text('SELECT 1'))
        return {'status':'ready','database':'ok','time_utc':datetime.now(timezone.utc).isoformat()}
    except Exception:
        raise HTTPException(503,'Database haipatikani')
@app.post('/auth/login',response_model=TokenOut)
def login(b:LoginIn,request:Request,db:Session=Depends(get_db)):
    username=b.username.lower()
    ip=request.client.host if request.client else 'unknown'
    user_key=f'user:{username}:ip:{ip}'
    ip_key=f'ip:{ip}'
    throttle(user_key,config.LOGIN_MAX_FAILS); throttle(ip_key,config.LOGIN_IP_MAX_FAILS)
    distributed_throttle(user_key,config.LOGIN_MAX_FAILS,config.LOGIN_WINDOW_S)
    distributed_throttle(ip_key,config.LOGIN_IP_MAX_FAILS,config.LOGIN_WINDOW_S)
    u=db.query(User).filter(User.username==username).first()
    if not u or not verify_password(b.password,u.password_hash):
        now=time.time(); FAILS[user_key].append(now); FAILS[ip_key].append(now)
        raise HTTPException(401,'Jina au nenosiri si sahihi')
    FAILS.pop(user_key,None); FAILS.pop(ip_key,None)
    raw_refresh=secrets.token_urlsafe(48)
    session=RefreshSession(
        id=str(uuid.uuid4()), user_id=u.id,
        token_hash=hashlib.sha256(raw_refresh.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc)+__import__('datetime').timedelta(days=config.REFRESH_TOKEN_DAYS),
    )
    db.add(session); audit(db,request,'auth.login',actor_id=u.id,outcome='success'); db.commit()
    return TokenOut(access_token=create_token(u.id),refresh_token=raw_refresh)

@app.post('/auth/refresh',response_model=TokenOut)
def refresh(b:RefreshIn,request:Request,db:Session=Depends(get_db)):
    token_hash=hashlib.sha256(b.refresh_token.encode()).hexdigest()
    session=db.query(RefreshSession).filter_by(token_hash=token_hash).first()
    now=datetime.now(timezone.utc)
    if not session or utc_aware(session.revoked_at) or utc_aware(session.expires_at)<=now:
        audit(db,request,'auth.refresh',outcome='denied')
        db.commit()
        raise HTTPException(401,'Refresh token si halali')
    raw_refresh=secrets.token_urlsafe(48)
    replacement=RefreshSession(
        id=str(uuid.uuid4()), user_id=session.user_id,
        token_hash=hashlib.sha256(raw_refresh.encode()).hexdigest(),
        expires_at=now+__import__('datetime').timedelta(days=config.REFRESH_TOKEN_DAYS),
    )
    session.revoked_at=now
    session.replaced_by=replacement.id
    db.add(replacement); audit(db,request,'auth.refresh',actor_id=session.user_id,outcome='success')
    db.commit()
    return TokenOut(access_token=create_token(session.user_id),refresh_token=raw_refresh)

@app.post('/auth/logout')
def logout(b:LogoutIn,user:User=Depends(current_user),request:Request=None,db:Session=Depends(get_db)):
    if b.refresh_token:
        token_hash=hashlib.sha256(b.refresh_token.encode()).hexdigest()
        session=db.query(RefreshSession).filter_by(token_hash=token_hash,user_id=user.id).first()
        if session and not session.revoked_at:
            session.revoked_at=datetime.now(timezone.utc)
    audit(db,request,'auth.logout',actor_id=user.id,outcome='success')
    db.commit()
    return {'ok':True}


@app.post('/auth/password-reset/request')
def password_reset_request(b:PasswordResetRequestIn,request:Request,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(username=b.username.lower()).first()
    if u:
        raw=secrets.token_urlsafe(48)
        row=PasswordResetToken(
            id=str(uuid.uuid4()), user_id=u.id,
            token_hash=hashlib.sha256(raw.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc)+timedelta(minutes=30),
        )
        db.add(row)
        audit(db,request,'auth.password_reset_requested',actor_id=u.id,outcome='success')
        db.commit()
    else:
        audit(db,request,'auth.password_reset_requested',outcome='not_found')
        db.commit()
    return {'ok':True,'detail':'If the account exists, reset instructions will be delivered by the configured account channel.'}


@app.post('/auth/password-reset/confirm')
def password_reset_confirm(b:PasswordResetConfirmIn,request:Request,db:Session=Depends(get_db)):
    token_hash=hashlib.sha256(b.token.encode()).hexdigest()
    row=db.query(PasswordResetToken).filter_by(token_hash=token_hash).first()
    now=datetime.now(timezone.utc)
    if not row or utc_aware(row.used_at) or utc_aware(row.expires_at)<=now:
        audit(db,request,'auth.password_reset_confirm',outcome='denied')
        db.commit()
        raise HTTPException(400,'Reset token si halali au imeisha muda')
    u=db.get(User,row.user_id)
    if not u:
        raise HTTPException(400,'Reset token si halali')
    u.password_hash=hash_password(b.password)
    row.used_at=now
    for session in db.query(RefreshSession).filter_by(user_id=u.id,revoked_at=None).all():
        session.revoked_at=now
    audit(db,request,'auth.password_reset_confirm',actor_id=u.id,outcome='success')
    db.commit()
    return {'ok':True}
@app.post('/admin/users',status_code=201)
def create_user(b:UserIn,admin:User=Depends(current_user),db:Session=Depends(get_db)):
    if admin.role!='admin': raise HTTPException(403,'Msimamizi tu')
    n=b.username.lower()
    if db.query(User).filter_by(username=n).first(): raise HTTPException(409,'Jina limeshatumika')
    u=User(id=str(uuid.uuid4()),username=n,password_hash=hash_password(b.password),role=b.role); db.add(u); db.commit(); return {'id':u.id,'username':n}
@app.post('/projects',status_code=201)
def new_project(b:ProjectIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    p=Project(id=str(uuid.uuid4()),name=b.name,projected_crs=b.projected_crs,created_by=user.id); db.add(p); db.add(ProjectMember(project_id=p.id,user_id=user.id,role='owner')); db.commit()
    return {'id':p.id,'name':p.name,'projected_crs':p.projected_crs}
@app.get('/projects')
def my_projects(user:User=Depends(current_user),db:Session=Depends(get_db)):
    q=db.query(Project) if user.role=='admin' else db.query(Project).join(ProjectMember,ProjectMember.project_id==Project.id).filter(ProjectMember.user_id==user.id)
    return [{'id':p.id,'name':p.name,'projected_crs':p.projected_crs} for p in q.all()]
@app.post('/projects/{pid}/members',status_code=201)
def add_member(pid:str,b:MemberIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    require_permission(db,user,pid,'manage_members')
    if b.role not in config.PROJECT_ROLES:
        raise HTTPException(400,'Nafasi ya mradi haijulikani')
    u=db.query(User).filter_by(username=b.username.lower()).first()
    if not u: raise HTTPException(404,'Mtumiaji hayupo')
    db.merge(ProjectMember(project_id=pid,user_id=u.id,role=b.role)); db.commit(); return {'ok':True}
@app.post('/sync/push',response_model=PushResponse)
def push(body:PushRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    for pid in {r.project_id for r in body.records}: require_permission(db,user,pid,'sync')
    acks=[]
    for it in sorted(body.records,key=lambda r:typed.PRIORITY.get(r.record_type,9)):
        h=sha(it.payload)
        old=db.query(Record).filter_by(project_id=it.project_id,record_uuid=it.record_uuid).first()
        if old:
            if old.content_hash==h: acks.append(PushAck(record_uuid=it.record_uuid,status='duplicate',server_version=old.server_version)); continue
            c=SyncConflict(project_id=it.project_id,record_uuid=it.record_uuid,device_id=it.device_id,incoming_json=canon(it.payload),existing_json=old.payload_json)
            db.add(c); db.flush(); acks.append(PushAck(record_uuid=it.record_uuid,status='conflict',server_version=old.server_version,conflict_id=c.id,detail='Maudhui tofauti na yaliyo kwenye seva')); continue
        err=typed.project(db,it)
        if err: acks.append(PushAck(record_uuid=it.record_uuid,status='invalid',detail=err[0],retry=err[1])); continue
        db.add(Record(project_id=it.project_id,record_uuid=it.record_uuid,record_type=it.record_type,payload_json=canon(it.payload),created_at_utc=it.created_at_utc,
            updated_at_utc=it.updated_at_utc,created_by=user.id,device_id=it.device_id,source_method=it.source_method,crs=it.crs,content_hash=h,client_hash=it.content_hash))
        db.flush(); acks.append(PushAck(record_uuid=it.record_uuid,status='accepted',server_version=1))
    db.commit(); return PushResponse(accepted=acks,server_time_utc=datetime.now(timezone.utc))
@app.get('/sync/pull',response_model=PullResponse)
def pull(project_id:str,cursor:int=0,limit:int=200,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if limit<1 or limit>500: raise HTTPException(400,'limit iwe 1..500')
    require_permission(db,user,project_id,'sync')
    rows=db.query(Record).filter(Record.project_id==project_id,Record.id>cursor).order_by(Record.id).limit(limit).all()
    return PullResponse(records=[{'record_uuid':r.record_uuid,'project_id':r.project_id,'record_type':r.record_type,'payload':json.loads(r.payload_json),
        'created_at_utc':r.created_at_utc.isoformat(),'updated_at_utc':r.updated_at_utc.isoformat(),'server_version':r.server_version,'crs':r.crs,
        'deleted_at_utc':r.deleted_at_utc.isoformat() if r.deleted_at_utc else None} for r in rows],
        next_cursor=rows[-1].id if rows else cursor)
@app.get('/projects/{pid}/analysis')
def analysis(pid:str,sample_type:str|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    ds=dataset.build(db,need_member(db,user,pid))
    allowed={'rock_chip','soil','stream_sediment','channel','surface'}
    if sample_type and sample_type not in allowed: raise HTTPException(400,'Aina ya sampuli haijulikani')
    tr,pl=quick(ds,sample_type)
    map_type=sample_type or tr.get('sample_type')
    rows=[x for x in ds['samples'] if not map_type or x.get('kind')==map_type]
    warnings=[DISCLAIMER,'Trend hutumia aina moja ya sampuli kwa wakati mmoja.','Mwelekeo wa 2D hutumia sampuli huru pekee; assay za downhole hazihamishwi hadi collar bila desurveying.']
    if not ds.get('qa_checks'): warnings.append('Hakuna QA/QC controls zilizowasilishwa; matokeo hayajathibitishwa kwa controls.')
    return {'samples':rows,'collars':ds['collars'],'trend':tr,'plane':pl,'crs':ds['crs'],'input_hash':ds['input_hash'],'qa_checks':ds.get('qa_checks',[]),'selected_sample_type':map_type,'warnings':warnings}

@app.get('/projects/{pid}/report.pdf')
def pdf(pid:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    ds=dataset.build(db,need_member(db,user,pid)); tr,pl=quick(ds)
    try:
        data,mt=report.to_pdf(report.build_html(user.username,ds['samples'],tr,pl,ds.get('qa_checks',[]),ds.get('input_hash')))
    except RuntimeError as exc:
        raise HTTPException(503,str(exc)) from exc
    if mt!='application/pdf': raise HTTPException(503,'PDF haipatikani; wasiliana na msimamizi.')
    return Response(data,media_type='application/pdf',headers={'Content-Disposition':'inline; filename=ripoti.pdf'})
@app.post('/attachments',status_code=201)
async def upload_attachment(project_id:str=Form(...),sample_id:str=Form(...),sample_record_uuid:str=Form(...),file:UploadFile=File(...),user:User=Depends(current_user),db:Session=Depends(get_db)):
    need_member(db,user,project_id)
    sid=sample_id.strip().upper()
    if not db.query(Sample).filter_by(project_id=project_id,sample_id=sid,record_uuid=sample_record_uuid).first():
        raise HTTPException(404,'Rekodi husika ya sampuli haijafika kwenye seva bado')
    allowed={'image/jpeg':'JPEG','image/png':'PNG','image/webp':'WEBP'}
    if file.content_type not in allowed: raise HTTPException(415,'Picha lazima iwe JPEG, PNG au WEBP')
    raw=await file.read(10*1024*1024+1)
    if not raw or len(raw)>10*1024*1024: raise HTTPException(413,'Picha isiwe zaidi ya MB 10')
    try:
        from PIL import Image,ImageOps
        Image.MAX_IMAGE_PIXELS=25_000_000
        with Image.open(io.BytesIO(raw)) as source:
            if source.format != allowed[file.content_type]: raise HTTPException(415,'Aina ya picha haifanani na maudhui ya faili')
            source.verify()
        with Image.open(io.BytesIO(raw)) as source:
            clean=ImageOps.exif_transpose(source)
            clean.thumbnail((4096,4096))
            if clean.mode not in ('RGB','RGBA'): clean=clean.convert('RGBA' if 'A' in clean.getbands() else 'RGB')
            fmt=allowed[file.content_type]
            if fmt=='JPEG' and clean.mode=='RGBA': clean=clean.convert('RGB')
            buf=io.BytesIO()
            opts={'quality':88,'optimize':True} if fmt=='JPEG' else {'optimize':True}
            clean.save(buf,format=fmt,**opts)
            data=buf.getvalue()
    except HTTPException: raise
    except ImportError as exc: raise HTTPException(503,'Image sanitizer haijasakinishwa; picha haijahifadhiwa.') from exc
    except Exception as exc: raise HTTPException(415,'Picha imeharibika au haiwezi kusafishwa.') from exc
    if not data or len(data)>10*1024*1024: raise HTTPException(413,'Picha iliyosafishwa imezidi MB 10')
    digest=hashlib.sha256(data).hexdigest()
    duplicate=db.query(Attachment).filter_by(project_id=project_id,sample_id=sid,sha256=digest).first()
    if duplicate:
        return {'id':duplicate.id,'sample_id':sid,'filename':duplicate.filename,'sha256':duplicate.sha256,'size_bytes':duplicate.size_bytes,'duplicate':True}
    ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[allowed[file.content_type]]
    storage_key=secrets.token_hex(24)+ext
    base=os.getenv('ATTACHMENTS_DIR',os.path.join(os.path.dirname(__file__),'..','data','attachments'))
    os.makedirs(base,exist_ok=True)
    final_path=os.path.join(base,storage_key); tmp_path=final_path+'.tmp'
    with open(tmp_path,'wb') as out: out.write(data)
    os.replace(tmp_path,final_path)
    row=Attachment(project_id=project_id,sample_id=sid,sample_record_uuid=sample_record_uuid,storage_key=storage_key,
        filename=os.path.basename(file.filename or 'picha'),media_type=file.content_type,sha256=digest,size_bytes=len(data),uploaded_by=user.id)
    try:
        db.add(row); db.commit(); db.refresh(row)
    except Exception:
        db.rollback()
        try: os.remove(final_path)
        except OSError: pass
        raise
    return {'id':row.id,'sample_id':sid,'filename':row.filename,'sha256':row.sha256,'size_bytes':row.size_bytes,'duplicate':False}
@app.get('/projects/{pid}/samples/{sample_id}/attachments')
def list_attachments(pid:str,sample_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    need_member(db,user,pid); rows=db.query(Attachment).filter_by(project_id=pid,sample_id=sample_id.strip().upper()).order_by(Attachment.id).all()
    return [{'id':a.id,'filename':a.filename,'media_type':a.media_type,'sha256':a.sha256,'size_bytes':a.size_bytes} for a in rows]
@app.get('/projects/{pid}/attachments/{attachment_id}')
def get_attachment(pid:str,attachment_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    need_member(db,user,pid); a=db.query(Attachment).filter_by(project_id=pid,id=attachment_id).first()
    if not a: raise HTTPException(404,'Picha haipo')
    base=os.getenv('ATTACHMENTS_DIR',os.path.join(os.path.dirname(__file__),'..','data','attachments')); path=os.path.join(base,a.storage_key)
    if not os.path.isfile(path): raise HTTPException(404,'Faili halipo kwenye hifadhi')
    return FileResponse(path,media_type=a.media_type,filename=a.filename)
@app.get('/engines')
def engines(user:User=Depends(current_user)):
    return [{'name':e.name,'version':e.version,'requires':e.requires,'library_installed':e.library_installed,'adapter_ready':e.adapter_ready,'warnings':e.warnings} for e in ENGINES.values()]
def run_job(job_id):
    db=SessionLocal(); j=db.get(Job,job_id)
    try:
        j.status='running'; j.started_at=utcnow(); db.commit()
        e=ENGINES[j.engine]; ds=dataset.build(db,db.get(Project,j.project_id)); params=json.loads(j.params_json); ds['_sample_type']=params.get('sample_type'); j.input_hash=ds['input_hash']; j.engine_version=e.version
        j.warnings_json=json.dumps([DISCLAIMER]+e.warnings)
        errs=e.validate(ds)+([] if e.adapter_ready else ['Adapter ya engine hii bado haijaandikwa'])+([] if e.library_installed else [f'Maktaba {e.requires} haijasakinishwa'])
        if errs: j.status='rejected'; j.error='; '.join(errs)
        else: j.result_json=json.dumps(e.run(ds,params),default=str); j.status='done'
    except Exception as ex: db.rollback(); j=db.get(Job,job_id); j.status='failed'; j.error=str(ex)[:500]
    j.finished_at=utcnow(); db.commit()
    final_status=j.status
    db.close()
    return {'job_id':job_id,'status':final_status}
@app.post('/jobs',status_code=202)
def new_job(b:JobIn,bg:BackgroundTasks,user:User=Depends(current_user),db:Session=Depends(get_db)):
    require_permission(db,user,b.project_id,'process')
    if b.engine not in ENGINES: raise HTTPException(400,'Engine haijulikani')
    params_hash=hashlib.sha256(canon({'project_id':b.project_id,'engine':b.engine,'params':b.params}).encode()).hexdigest()
    existing=db.query(Job).filter_by(project_id=b.project_id,engine=b.engine,params_json=json.dumps(b.params),requested_by=user.id).first()
    if existing:
        return {'id':existing.id,'status':existing.status,'deduplicated':True,'input_hash':existing.input_hash}
    j=Job(id=str(uuid.uuid4()),project_id=b.project_id,engine=b.engine,params_json=json.dumps(b.params),requested_by=user.id); db.add(j); db.commit()
    if config.REDIS_URL:
        try:
            from redis import Redis
            from rq import Queue
            queue=Queue('chimbasmart',connection=Redis.from_url(config.REDIS_URL))
            queue.enqueue('app.worker.execute_job',j.id,job_timeout='30m',failure_ttl=86400,retries=0,job_id=j.id)
            audit(db,None,'job.queued',actor_id=user.id,project_id=j.project_id,resource_type='job',resource_id=j.id)
            db.commit()
        except Exception as exc:
            j.status='failed'; j.error='Durable queue unavailable'; j.finished_at=utcnow(); db.commit()
            audit(db,None,'job.queue_failed',actor_id=user.id,project_id=j.project_id,resource_type='job',resource_id=j.id,outcome='failed',details={'error':'queue unavailable'})
            db.commit()
            raise HTTPException(503,'Mfumo wa kazi haupatikani') from exc
    else:
        bg.add_task(run_job,j.id)
    return {'id':j.id,'status':'queued','deduplicated':False}
@app.get('/jobs/{jid}')
def get_job(jid:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    j=db.get(Job,jid)
    if not j: raise HTTPException(404,'Kazi haipo')
    need_member(db,user,j.project_id)
    return {'id':j.id,'engine':j.engine,'engine_version':j.engine_version,'status':j.status,'input_hash':j.input_hash,'params':json.loads(j.params_json),
        'result':json.loads(j.result_json) if j.result_json else None,'warnings':json.loads(j.warnings_json or '[]'),'error':j.error,'review_state':j.review_state,
        'started_at':j.started_at,'finished_at':j.finished_at}
_F=os.getenv('FRONTEND_DIR') or next((p for p in (os.path.join(os.path.dirname(__file__),'..','..','frontend'),'frontend') if os.path.isdir(p)),None)
if _F: app.mount('/',StaticFiles(directory=_F,html=True))
