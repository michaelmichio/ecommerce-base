import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from uuid import UUID, uuid4
from typing import List

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, ProductListResponse
from app.core.dependencies import get_current_user
from app.core.rbac import require_role
from app.models.user import User
from app.api.routes.upload import UPLOAD_DIR
from app.core.utils import delete_file_safe
from app.schemas.search import ProductSearchRequest
from app.core.advanced_query import apply_filters, apply_search, apply_sort

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/search", response_model=ProductListResponse)
def search_products(
    body: ProductSearchRequest,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # 🔍 Filtering
    query = apply_filters(query, body.filters)

    # 🔎 Search
    query = apply_search(query, body.search)

    # 🔢 Sorting
    query = apply_sort(query, body.sort)

    # 📄 Pagination
    total = query.count()
    products = query.offset((body.page - 1) * body.limit).limit(body.limit).all()

    return {
        "page": body.page,
        "limit": body.limit,
        "total": total,
        "pages": (total + body.limit - 1) // body.limit,
        "items": products,
    }

# 🟢 List all products
@router.get("/", response_model=ProductListResponse)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("created_desc", description="created_asc | created_desc | price_asc | price_desc")
):
    """
    Simple public product listing (fast and cache-friendly)
    """

    query = db.query(Product)

    # Sorting
    if sort == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort == "price_desc":
        query = query.order_by(desc(Product.price))
    elif sort == "created_asc":
        query = query.order_by(asc(Product.created_at))
    else:
        query = query.order_by(desc(Product.created_at))

    # Pagination
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "items": products,
    }

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

    # Hapus semua file fisik milik produk
    if product.images:
        for image_url in product.images:
            filename = os.path.basename(image_url)
            file_path = os.path.join(UPLOAD_DIR, filename)
            delete_file_safe(file_path, UPLOAD_DIR)


    db.delete(product)
    db.commit()
    return None


@router.post("/{product_id}/images")
async def upload_product_images(
    product_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    urls = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not an image")
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid4()}{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        urls.append(f"/upload/{filename}")

    product.images = (product.images or []) + urls
    db.commit()
    db.refresh(product)
    return {"message": "Images attached", "images": product.images}

@router.delete("/{product_id}/images")
def delete_product_image(
    product_id: UUID,
    image_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.images or image_url not in product.images:
        raise HTTPException(status_code=404, detail="Image not found in product")

    # Hapus URL dari database
    product.images = [img for img in product.images if img != image_url]
    db.commit()
    db.refresh(product)

    # Hapus file fisik secara aman
    filename = os.path.basename(image_url)
    file_path = os.path.join(UPLOAD_DIR, filename)
    delete_file_safe(file_path, UPLOAD_DIR)

    return {"message": f"Deleted image {filename}", "remaining_images": product.images}
