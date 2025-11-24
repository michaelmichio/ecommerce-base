from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/users", tags=["users"])


def success(data):
    return SuccessResponse(data=data)


@router.get("/me", response_model=SuccessResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Return the authenticated user's profile.
    Using HttpOnly Cookie Auth system:
    - User is retrieved via get_current_user()
    - Role is standardized as string (role_name)
    """

    return success({
        "id": str(current_user.id),
        "email": current_user.email,
        "role": getattr(current_user, "role_name", "user"),
        "is_active": current_user.is_active,
    })
