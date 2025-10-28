from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.core.dependencies import get_current_user
from app.core.rbac import require_role
from app.models.user import User

router = APIRouter(prefix="/products", tags=["products"])

# 🟢 List all products
@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return products

# 🟢 Get product detail
@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 🔒 Create new product (admin only)
@router.post("/", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    product = Product(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        images=payload.images,
        stock=payload.stock,
        price=payload.price,
        discount=payload.discount,
        status=payload.status,
        created_by_id=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# 🔒 Update product (admin only)
@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

# 🔒 Delete product (admin only)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None
