from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.schemas.response import SuccessResponse
from app.schemas.user import UserCreate, UserOut, LoginPayload
from app.models.user import User
from app.core.config import settings

from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["auth"])


# ==============================================================================
# 🧰 Cookie Helpers
# ==============================================================================

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """
    Set HttpOnly cookies for access_token and refresh_token.
    These cookies will be automatically sent by the browser and can be
    read by the Next.js middleware for server-side auth.
    """
    secure = (settings.ENV == "production")

    # Access token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_EXPIRE_MINUTES * 60,
    )

    # Refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=settings.REFRESH_EXPIRE_DAYS * 86400,
    )


def clear_auth_cookies(response: Response):
    """
    Clear authentication cookies on logout.
    """
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


# ==============================================================================
# 🟦 REGISTER
# ==============================================================================

@router.post("/register", response_model=SuccessResponse)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return SuccessResponse(data=UserOut.model_validate(new_user))


# ==============================================================================
# 🟩 LOGIN  (HttpOnly Cookie Version)
# ==============================================================================

@router.post("/login", response_model=SuccessResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    """
    Login using email/password.
    - Verifies password
    - Issues access & refresh tokens (stored as HttpOnly cookies)
    - Returns generic success response (never returns raw tokens)
    """

    # Find user
    user = db.query(User).filter(User.email == payload.email).first()

    # bcrypt limitation: max 72 bytes
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 bytes)")

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Determine role (string or relationship-safe)
    if hasattr(user.role, "name"):
        role_name = user.role.name
    else:
        role_name = user.role if user.role else "user"

    # Create tokens
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": role_name},
        expires_delta=timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES),
    )

    refresh_token = create_refresh_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_EXPIRE_DAYS),
    )

    # Build response
    body = SuccessResponse(
        data={
            "id": str(user.id),
            "email": user.email
        }
    ).model_dump()
    response = JSONResponse(content=body)

    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)

    return response


# ==============================================================================
# 🔄 REFRESH TOKEN
# ==============================================================================

@router.post("/refresh", response_model=SuccessResponse)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """
    Issues a new access token using the refresh_token HttpOnly cookie.
    - Frontend NEVER sends refresh token manually (cookie only)
    - The returned access token is also set as a HttpOnly cookie
    """

    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_refresh_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine user role
    if hasattr(user.role, "name"):
        role_name = user.role.name
    else:
        role_name = user.role if user.role else "user"

    # Issue new access token
    new_access = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": role_name},
        expires_delta=timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES),
    )

    # Return response
    body = SuccessResponse(data={"message": "Token refreshed"}).model_dump()
    response = JSONResponse(content=body)

    # Replace old cookie
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=(settings.ENV == "production"),
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_EXPIRE_MINUTES * 60,
    )

    return response


# ==============================================================================
# 🚪 LOGOUT
# ==============================================================================

@router.post("/logout", response_model=SuccessResponse)
def logout():
    """
    Clears auth cookies and logs out the user.
    """

    body = SuccessResponse(data={"message": "Logged out"}).model_dump()
    response = JSONResponse(content=body)

    clear_auth_cookies(response)
    return response
