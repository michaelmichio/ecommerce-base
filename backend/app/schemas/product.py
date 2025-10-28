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

class ProductOut(ProductBase):
    id: UUID
    created_by_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
