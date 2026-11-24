import os
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./chimbasmart_dev.db')
ENV=os.getenv('ENV','dev')
JWT_SECRET=os.getenv('JWT_SECRET','')
if not JWT_SECRET:
    if ENV=='prod': raise RuntimeError('JWT_SECRET inahitajika kwenye prod')
    JWT_SECRET='dev-only-secret-not-for-production-0123456789'
JWT_ALGORITHM='HS256'
ACCESS_TOKEN_MINUTES=int(os.getenv('ACCESS_TOKEN_MINUTES','43200'))  # siku 30; refresh/revocation bado inahitajika kabla ya production kubwa
AUTO_CREATE_TABLES=os.getenv('AUTO_CREATE_TABLES','1' if DATABASE_URL.startswith('sqlite') else '0')=='1'
LOGIN_MAX_FAILS=5; LOGIN_IP_MAX_FAILS=30; LOGIN_WINDOW_S=900
