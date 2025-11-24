from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# ===================================================================
# Base used only for creation
# ===================================================================
class ProductBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    images: Optional[List[str]] = []
    stock: int
    price: Decimal
    discount: Optional[float] = 0.0
    status: Optional[str] = "active"


class ProductCreate(ProductBase):
    """Schema for creating a product (all fields required)."""
    pass


# ===================================================================
# Update schema: ALL fields optional (very important)
# ===================================================================
class ProductUpdate(BaseModel):
    """Schema for updating product fields (all optional)."""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = []
    stock: Optional[int] = None
    price: Optional[Decimal] = None
    discount: Optional[float] = None
    status: Optional[str] = None


# ===================================================================
# Output schema
# ===================================================================
class ProductOut(BaseModel):
    id: UUID
    name: str
    category: Optional[str]
    description: Optional[str]
    price: Decimal
    stock: int
    discount: Optional[float]
    status: str
    images: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class ProductListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    items: List[ProductOut]
