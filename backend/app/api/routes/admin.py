from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.rbac import require_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):
    """
    Admin-only dashboard.
    Uses RBAC with HttpOnly cookie authentication.
    """
    return {
        "message": f"Welcome admin {current_user.email}!",
        "role": current_user.role_name
    }
