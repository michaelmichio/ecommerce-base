# app/core/dependencies.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.jwt import verify_access_token
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency untuk mengambil user yang sedang login.
    Akan raise 401 jika token invalid, expired, atau user tidak ditemukan.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise credentials_exception

    # opsional: simpan role dari token ke objek user (jika mau dipakai langsung)
    user.role_name = payload.get("role", getattr(user.role, "name", "user"))

    return user
