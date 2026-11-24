import bcrypt, jwt
from datetime import datetime,timedelta,timezone
from .config import JWT_SECRET,JWT_ALGORITHM,ACCESS_TOKEN_MINUTES
def hash_password(p:str)->str: return bcrypt.hashpw(p.encode()[:72],bcrypt.gensalt()).decode()
def verify_password(p:str,h:str)->bool:
    try: return bcrypt.checkpw(p.encode()[:72],h.encode())
    except ValueError: return False
def create_token(uid:str)->str:
    return jwt.encode({'sub':uid,'exp':datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_MINUTES),'type':'access','jti':__import__('uuid').uuid4().hex},JWT_SECRET,algorithm=JWT_ALGORITHM)
def decode_token(t:str)->dict: return jwt.decode(t,JWT_SECRET,algorithms=[JWT_ALGORITHM])  # inatupa jwt.PyJWTError
