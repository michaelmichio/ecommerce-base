from app.core.config import settings
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Membuat JWT access token dengan payload berisi user info.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ACCESS_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Memverifikasi JWT access token dan mengembalikan payload.
    Jika token invalid atau expired, return None.
    """
    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET, algorithms=[ALGORITHM])
        # Optional check: pastikan token belum kedaluwarsa
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None
        return payload
    except JWTError:
        return None
