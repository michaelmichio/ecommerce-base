from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.models.user import User


def require_role(required_role: str):
    """
    Role-based access control dependency.
    Ensures the current user has the specified role.

    Works with:
    - Relationship role (user.role.name)
    - String role (user.role)
    - Computed role_name from dependencies.py
    """

    def role_checker(current_user: User = Depends(get_current_user)):
        # Pull role in a safe and unified way
        user_role = getattr(current_user, "role_name", None)

        if not user_role or user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires role: {required_role}",
            )

        return current_user

    return role_checker
