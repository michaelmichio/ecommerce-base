from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.jwt import decode_access_token
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get the currently authenticated user using HttpOnly cookie-based access token.

    - Reads "access_token" from request.cookies (secure from JS)
    - Decodes token using decode_access_token() from app.core.jwt
    - Ensures token is valid, not expired, and type == "access"
    - Loads user from database
    - Returns user instance
    """

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Decode access token
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Load user from DB
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Attach token role (if present) for easy access
    # Role may come from DB or token
    payload_role = payload.get("role")

    if hasattr(user.role, "name"):
        user.role_name = user.role.name
    else:
        user.role_name = payload_role or user.role or "user"

    return user
