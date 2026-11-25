import bcrypt
from app.security import hash_password,verify_password


def test_versioned_bcrypt_uses_full_password():
    password='A'*72+'expected suffix'
    stored=hash_password(password)
    assert stored.startswith('bcrypt-sha256$')
    assert verify_password(password,stored)
    assert not verify_password('A'*72+'different suffix',stored)


def test_legacy_bcrypt_hashes_reject_passwords_at_truncation_boundary():
    legacy_71=bcrypt.hashpw(b'A'*71,bcrypt.gensalt()).decode()
    legacy_72=bcrypt.hashpw(b'A'*72,bcrypt.gensalt()).decode()
    assert verify_password('A'*71,legacy_71)
    assert not verify_password('A'*71+'X',legacy_71)
    assert not verify_password('A'*72,legacy_72)
    assert not verify_password('A'*72+'suffix',legacy_72)


def test_legacy_password_limit_counts_utf8_bytes():
    password='é'*36
    legacy=bcrypt.hashpw(password.encode('utf-8')[:72],bcrypt.gensalt()).decode()
    assert not verify_password(password,legacy)
