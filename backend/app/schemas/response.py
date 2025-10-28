from pydantic import BaseModel
from typing import Optional, Any

# 🔹 Struktur standar untuk error
class ErrorDetail(BaseModel):
    code: int
    type: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# 🔹 Struktur standar untuk success
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
