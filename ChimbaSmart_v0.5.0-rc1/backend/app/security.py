import bcrypt, hashlib, jwt
from datetime import datetime,timedelta,timezone
from .config import JWT_SECRET,JWT_ALGORITHM,ACCESS_TOKEN_MINUTES

_BCRYPT_SHA256_PREFIX='bcrypt-sha256$'

def _password_bytes(p:str)->bytes:
    return hashlib.sha256(p.encode('utf-8')).digest()

def hash_password(p:str)->str:
    return _BCRYPT_SHA256_PREFIX+bcrypt.hashpw(_password_bytes(p),bcrypt.gensalt()).decode()

def verify_password(p:str,h:str)->bool:
    try:
        if h.startswith(_BCRYPT_SHA256_PREFIX):
            password=_password_bytes(p)
            stored_hash=h[len(_BCRYPT_SHA256_PREFIX):].encode('ascii')
        else:
            password=p.encode('utf-8')
            if len(password)>=72:
                return False
            stored_hash=h.encode('ascii')
        return bcrypt.checkpw(password,stored_hash)
    except (ValueError,TypeError,UnicodeEncodeError):
        return False
def create_token(uid:str,session_id:str|None=None,auth_version:int=0)->str:
    claims={'sub':uid,'exp':datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_MINUTES),'type':'access','jti':__import__('uuid').uuid4().hex,'ver':auth_version}
    if session_id:
        claims['sid']=session_id
    return jwt.encode(claims,JWT_SECRET,algorithm=JWT_ALGORITHM)
def decode_token(t:str)->dict:
    payload=jwt.decode(t,JWT_SECRET,algorithms=[JWT_ALGORITHM])
    if payload.get('type')!='access':
        raise jwt.InvalidTokenError('Token si access token')
    return payload
