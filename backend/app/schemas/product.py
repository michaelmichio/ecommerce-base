from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    images: Optional[List[str]] = None
    stock: int
    price: float
    discount: Optional[float] = 0.0
    status: Optional[str] = "active"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(BaseModel):
    id: UUID
    name: str
    category: Optional[str]
    description: Optional[str]
    price: float
    stock: int
    discount: Optional[float]
    status: str
    images: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

class ProductListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    items: List[ProductOut]

