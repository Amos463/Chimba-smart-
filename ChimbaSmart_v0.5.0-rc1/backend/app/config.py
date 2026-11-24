import os
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./chimbasmart_dev.db')
ENV=os.getenv('ENV','dev')
JWT_SECRET=os.getenv('JWT_SECRET','')
if not JWT_SECRET:
    if ENV=='prod': raise RuntimeError('JWT_SECRET inahitajika kwenye prod')
    JWT_SECRET='dev-only-secret-not-for-production-0123456789'
JWT_ALGORITHM='HS256'
ACCESS_TOKEN_MINUTES=int(os.getenv('ACCESS_TOKEN_MINUTES','15'))
REFRESH_TOKEN_DAYS=int(os.getenv('REFRESH_TOKEN_DAYS','7'))
MAX_REQUEST_BYTES=int(os.getenv('MAX_REQUEST_BYTES','10485760'))
REDIS_URL=os.getenv('REDIS_URL','')
CORS_ORIGINS=[x.strip() for x in os.getenv('CORS_ORIGINS','').split(',') if x.strip()]
AUTO_CREATE_TABLES=os.getenv('AUTO_CREATE_TABLES','1' if DATABASE_URL.startswith('sqlite') else '0')=='1'
LOGIN_MAX_FAILS=5; LOGIN_IP_MAX_FAILS=30; LOGIN_WINDOW_S=900

PROJECT_ROLES={
    'organization_admin','project_manager','geologist','field_technician',
    'laboratory_reviewer','read_only','owner','member','admin',
}
PROJECT_ROLE_PERMISSIONS={
    'owner':{'manage_project','manage_members','create','update','delete','sync','process','report','review'},
    'project_manager':{'manage_project','manage_members','create','update','delete','sync','process','report','review'},
    'organization_admin':{'manage_project','manage_members','create','update','delete','sync','process','report','review'},
    'geologist':{'create','update','sync','process','report','review'},
    'laboratory_reviewer':{'create','update','sync','process','report','review'},
    'field_technician':{'create','update','sync','report'},
    'read_only':{'report'},
    'member':{'create','update','sync','process','report'},
    'admin':{'manage_project','manage_members','create','update','delete','sync','process','report','review'},
}
