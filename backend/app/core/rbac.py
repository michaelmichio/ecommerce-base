from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.models.user import User

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.role or current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_dependency
