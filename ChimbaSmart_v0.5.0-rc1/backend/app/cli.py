"""python -m app.cli create-user <jina> <nenosiri> [--role admin]"""
import sys,uuid
from .db import Base,engine,SessionLocal
from .models import User
from .security import hash_password
def main():
    a=sys.argv[1:]
    if len(a)<3 or a[0]!='create-user' or len(a[2])<8: sys.exit(__doc__+'\nNenosiri angalau herufi 8.')
    Base.metadata.create_all(bind=engine); db=SessionLocal()
    role=a[a.index('--role')+1] if '--role' in a else 'field_user'
    db.add(User(id=str(uuid.uuid4()),username=a[1].lower(),password_hash=hash_password(a[2]),role=role)); db.commit(); print('Imeundwa:',a[1],role)
main()
