from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from ..db import get_db
from ..models import Cart, CartItem, Product
from ..schemas import CartOut, CartCreateIn, CartPatchIn

router = APIRouter(prefix="/carts", tags=["carts"])

@router.post("", response_model=CartOut, status_code=201)
def create_cart(payload: CartCreateIn, db: Session = Depends(get_db)):
    # Validate products exist
    product_ids = [i.product_id for i in payload.items]
    if not product_ids:
        raise HTTPException(status_code=400, detail="No items provided")
    existing = db.execute(select(Product.id).where(Product.id.in_(product_ids))).scalars().all()
    missing = sorted(set(product_ids) - set(existing))
    if missing:
        raise HTTPException(status_code=404, detail=f"Products not found: {missing}")

    cart = Cart()
    db.add(cart)
    db.flush()  # get cart.id

    # Upsert-like: for initial create, just add items with qty>0
    for it in payload.items:
        if it.qty <= 0:
            continue
        db.add(CartItem(cart_id=cart.id, product_id=it.product_id, qty=it.qty))

    db.commit()
    db.refresh(cart)
    return cart

@router.patch("/{cart_id}", response_model=CartOut)
def patch_cart(cart_id: int, payload: CartPatchIn, db: Session = Depends(get_db)):
    cart = db.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    product_ids = [i.product_id for i in payload.items]
    if not product_ids:
        return cart

    existing = db.execute(select(Product.id).where(Product.id.in_(product_ids))).scalars().all()
    missing = sorted(set(product_ids) - set(existing))
    if missing:
        raise HTTPException(status_code=404, detail=f"Products not found: {missing}")

    # Load existing items for this cart
    existing_items = {ci.product_id: ci for ci in cart.items}

    for change in payload.items:
        if change.qty == 0:
            # delete if exists
            if change.product_id in existing_items:
                db.delete(existing_items[change.product_id])
        else:
            if change.product_id in existing_items:
                existing_items[change.product_id].qty = change.qty
            else:
                db.add(CartItem(cart_id=cart.id, product_id=change.product_id, qty=change.qty))

    db.commit()
    db.refresh(cart)
    return cart
