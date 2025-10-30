from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/users", tags=["users"])

def success(data):
    return SuccessResponse(data=data)

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return success({
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    })
