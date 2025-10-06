from pydantic import BaseModel, Field
from typing import List, Optional

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = ""
    price: float
    stock: int
    class Config:
        from_attributes = True

class CartItemIn(BaseModel):
    product_id: int
    qty: int = Field(..., gt=-1)  # allow 0 for deletion in PATCH

class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    qty: int
    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    class Config:
        from_attributes = True

class CartCreateIn(BaseModel):
    items: List[CartItemIn]

class CartPatchIn(BaseModel):
    items: List[CartItemIn]
