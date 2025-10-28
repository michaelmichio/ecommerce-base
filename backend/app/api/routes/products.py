import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.core.dependencies import get_current_user
from app.core.rbac import require_role
from app.models.user import User
from app.api.routes.upload import UPLOAD_DIR

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

    # Hapus semua file fisik milik produk
    if product.images:
        for image_url in product.images:
            filename = os.path.basename(image_url)
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                # ✅ gunakan validasi path aman di sini juga
                file_path = os.path.abspath(file_path)
                if file_path.startswith(UPLOAD_DIR) and os.path.exists(file_path):
                    os.remove(file_path)


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
    if os.path.exists(file_path):
        # ✅ pastikan path aman sebelum hapus
        file_path = os.path.abspath(file_path)
        if file_path.startswith(UPLOAD_DIR) and os.path.exists(file_path):
            os.remove(file_path)


    return {"message": f"Deleted image {filename}", "remaining_images": product.images}
