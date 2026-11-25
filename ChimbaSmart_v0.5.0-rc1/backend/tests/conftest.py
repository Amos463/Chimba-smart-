import atexit,os,shutil,tempfile,uuid,pytest
TEST_STORAGE_DIR=tempfile.mkdtemp(prefix='chimbasmart-tests-')
atexit.register(shutil.rmtree,TEST_STORAGE_DIR,ignore_errors=True)
os.environ['DATABASE_URL']=f'sqlite:///{TEST_STORAGE_DIR}/t.db'
os.environ['ATTACHMENTS_DIR']=os.path.join(TEST_STORAGE_DIR,'attachments')
os.environ['JWT_SECRET']='test-only-chimbasmart-jwt-secret'
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models import User
from app.security import hash_password
PW='Parola-12345'
def mkuser(role='field_user'):
    db=SessionLocal(); n='u'+uuid.uuid4().hex[:8]; db.add(User(id=str(uuid.uuid4()),username=n,password_hash=hash_password(PW),role=role)); db.commit(); db.close(); return n
def hdr(c,n,pw=PW): return {'Authorization':'Bearer '+c.post('/auth/login',json={'username':n,'password':pw}).json()['access_token']}
def rec(pid,t,p):
    now='2026-11-23T10:00:00Z'
    return {'record_uuid':str(uuid.uuid4()),'project_id':pid,'record_type':t,'payload':p,'created_at_utc':now,'updated_at_utc':now,'device_id':'d','source_method':'test','crs':'EPSG:4326','content_hash':'0'*64}
def collar(h,i): return {'hole_id':h,'kind':'pit','lat':-3.0,'lon':32.1+i*0.001,'depth_m':3.0}
def assay(h,g,a=0,b=3): return {'hole_id':h,'from_m':a,'to_m':b,'kind':'assay','value_num':g,'unit':'g/t'}
@pytest.fixture(scope='session')
def client():
    with TestClient(app) as c: yield c
@pytest.fixture
def ctx(client):
    h=hdr(client,mkuser()); return h,client.post('/projects',json={'name':'T'},headers=h).json()['id']
