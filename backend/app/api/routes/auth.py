from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password
from app.schemas.response import SuccessResponse
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def success(data):
    return SuccessResponse(data=data)


def create_token(data: dict, secret: str, expires_delta: timedelta):
    """Helper untuk membuat JWT token dengan expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm="HS256")


@router.post("/login", response_model=SuccessResponse)
def login(payload: dict, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload["email"]).first()

    if not user or not verify_password(payload["password"], user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # pastikan role tidak None
    role_name = user.role.name if getattr(user, "role", None) else "user"

    # JWT payload berisi role dan email
    access_token = create_token(
        {"sub": str(user.id), "email": user.email, "role": role_name},
        settings.ACCESS_SECRET,
        timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"sub": str(user.id)},
        settings.REFRESH_SECRET,
        timedelta(days=settings.REFRESH_EXPIRE_DAYS),
    )

    # set refresh token cookie aman
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=(settings.ENV == "production"),
        samesite="lax",
        path="/",
        max_age=settings.REFRESH_EXPIRE_DAYS * 86400,
    )

    return success({"access_token": access_token})


@router.post("/refresh", response_model=SuccessResponse)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Menerbitkan ulang access token baru dari refresh token cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Ambil ulang data user untuk memuat role terbaru
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_name = user.role.name if getattr(user, "role", None) else "user"

    # ✅ Sekarang access token baru juga punya field role
    new_access = create_token(
        {"sub": str(user.id), "email": user.email, "role": role_name},
        settings.ACCESS_SECRET,
        timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES),
    )

    return success({"access_token": new_access})
