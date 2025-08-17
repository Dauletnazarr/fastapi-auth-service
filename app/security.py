import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_EXPIRE_MIN = settings.access_token_expire_minutes
REFRESH_EXPIRE_DAYS = settings.refresh_token_expire_days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_token(token: str) -> str:
    return pwd_context.hash(token)

def verify_token_hash(token: str, token_hash: str) -> bool:
    return pwd_context.verify(token, token_hash)

def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    exp = datetime.utcnow() + timedelta(minutes=expires_minutes or ACCESS_EXPIRE_MIN)
    payload = {"sub": subject, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str):
    exp = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    payload = {"sub": subject, "exp": exp, "typ": "refresh", "jti": jti}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, exp, jti

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e
