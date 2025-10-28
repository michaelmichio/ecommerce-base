import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from uuid import UUID, uuid4
from typing import List

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.core.rbac import require_role
from app.models.user import User
from app.api.routes.upload import UPLOAD_DIR
from app.core.utils import delete_file_safe
from app.schemas.search import ProductSearchRequest
from app.core.advanced_query import apply_filters, apply_search, apply_sort
from app.schemas.response import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/products", tags=["products"])

# 🧠 helper agar kode rapi
def success(data):
    return {"success": True, "data": data}


# 🟢 SEARCH (advanced)
@router.post("/search", response_model=SuccessResponse)
def search_products(
    body: ProductSearchRequest,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    query = apply_filters(query, body.filters)
    query = apply_search(query, body.search)
    query = apply_sort(query, body.sort)

    total = query.count()
    products = query.offset((body.page - 1) * body.limit).limit(body.limit).all()

    return success({
        "page": body.page,
        "limit": body.limit,
        "total": total,
        "pages": (total + body.limit - 1) // body.limit,
        "items": products,
    })


# 🟢 LIST (simple public)
@router.get("/", response_model=SuccessResponse)
def list_products(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    sort: str = "created_desc"
):
    query = db.query(Product)
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return success({
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "items": [ProductOut.from_orm(p) for p in products],
    })


# 🟢 DETAIL
@router.get("/{product_id}", response_model=SuccessResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return success(ProductOut.from_orm(product))


# 🔒 CREATE
@router.post("/", response_model=SuccessResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return success(new_product)


# 🔒 UPDATE
@router.put("/{product_id}", response_model=SuccessResponse)
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
    return success(product)


# 🔒 DELETE
@router.delete("/{product_id}", response_model=SuccessResponse)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Hapus semua file gambar produk (jika ada)
    if product.images:
        for image_url in product.images:
            filename = os.path.basename(image_url)
            file_path = os.path.join(UPLOAD_DIR, filename)
            delete_file_safe(file_path, UPLOAD_DIR)

    db.delete(product)
    db.commit()

    return success({"deleted_id": str(product_id)})


# 🔒 UPLOAD IMAGE
@router.post("/{product_id}/images", response_model=SuccessResponse)
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
    return success({"images": product.images})


# 🔒 DELETE IMAGE
@router.delete("/{product_id}/images", response_model=SuccessResponse)
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

    product.images = [img for img in product.images if img != image_url]
    db.commit()
    db.refresh(product)

    filename = os.path.basename(image_url)
    file_path = os.path.join(UPLOAD_DIR, filename)
    delete_file_safe(file_path, UPLOAD_DIR)

    return success({"remaining_images": product.images})
