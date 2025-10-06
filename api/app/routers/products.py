from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import Product
from ..schemas import ProductOut

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[ProductOut])
def list_products(q: str = Query(default=None, description="Buscar por nombre/descr."), db: Session = Depends(get_db)):
    stmt = select(Product)
    if q:
        ilike = f"%{q}%"
        stmt = stmt.where((Product.name.ilike(ilike)) | (Product.description.ilike(ilike)))
    stmt = stmt.order_by(Product.id.asc()).limit(200)
    return db.execute(stmt).scalars().all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
