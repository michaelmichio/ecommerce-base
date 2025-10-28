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
    description: Optional[str]
    category: Optional[str]
    price: float
    stock: Optional[int]
    discount: Optional[float]
    status: Optional[str]
    images: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # ✅ penting agar bisa from_orm(Product)

class ProductListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    items: List[ProductOut]

