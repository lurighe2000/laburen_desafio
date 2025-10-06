import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import delete
from .db import SessionLocal, engine
from .models import Product
from .db import Base

load_dotenv()

def pick_first_numeric(row, candidates):
    for c in candidates:
        if c in row and pd.notna(row[c]):
            try:
                v = float(str(row[c]).replace(",", "."))
                return v
            except Exception:
                pass
    return 0.0

def to_int_safe(v):
    if pd.isna(v):
        return 0
    try:
        return int(float(str(v).replace(",", ".")))
    except Exception:
        s = str(v).strip().lower()
        if s in ("si","sí","true","1","yes"):
            return 1
        if s in ("no","false","0"):
            return 0
        return 0

def seed_products(xlsx_path: str):
    print(f"Loading {xlsx_path}...")
    df = pd.read_excel(xlsx_path)

    # Normalizamos encabezados a UPPER
    norm = {c: str(c).strip().upper() for c in df.columns}
    df.rename(columns=norm, inplace=True)

    tipo_col   = "TIPO_PRENDA" if "TIPO_PRENDA" in df.columns else None
    talla_col  = "TALLA" if "TALLA" in df.columns else None
    color_col  = "COLOR" if "COLOR" in df.columns else None
    desc_col   = "DESCRIPCIÓN" if "DESCRIPCIÓN" in df.columns else ("DESCRIPCION" if "DESCRIPCION" in df.columns else None)
    cat_col    = "CATEGORÍA" if "CATEGORÍA" in df.columns else ("CATEGORIA" if "CATEGORIA" in df.columns else None)
    stock_col  = "CANTIDAD_DISPONIBLE" if "CANTIDAD_DISPONIBLE" in df.columns else ("DISPONIBLE" if "DISPONIBLE" in df.columns else None)
    price_cols = [c for c in ["PRECIO_50_U","PRECIO_100_U","PRECIO_200_U"] if c in df.columns]

    def build_name(row):
        parts = []
        for c in (tipo_col, color_col, talla_col):
            if c and c in row and pd.notna(row[c]):
                parts.append(str(row[c]).strip())
        if parts:
            return " ".join(parts)
        # fallback
        if "ID" in row and pd.notna(row["ID"]):
            return f"Producto {row['ID']}"
        return "Producto"

    def build_desc(row):
        cat = str(row[cat_col]).strip() if cat_col and pd.notna(row.get(cat_col)) else ""
        desc = str(row[desc_col]).strip() if desc_col and pd.notna(row.get(desc_col)) else ""
        return f"{cat} — {desc}" if cat and desc else (cat or desc or "")

    def build_price(row):
        return pick_first_numeric(row, price_cols) if price_cols else 0.0

    def build_stock(row):
        if stock_col and stock_col in row:
            return to_int_safe(row[stock_col])
        return 0

    out = pd.DataFrame()
    out["name"] = df.apply(build_name, axis=1).fillna("Producto").replace({"": "Producto"})
    out["description"] = df.apply(build_desc, axis=1).fillna("")
    out["price"] = pd.to_numeric(df.apply(build_price, axis=1), errors="coerce").fillna(0.0)
    out["stock"] = pd.to_numeric(df.apply(build_stock, axis=1), errors="coerce").fillna(0).astype(int)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(Product))
        db.commit()
        objs = [Product(name=r.name, description=r.description, price=float(r.price), stock=int(r.stock)) for r in out.itertuples(index=False)]
        db.add_all(objs)
        db.commit()
    print(f"Seeded {len(objs)} products.")

if __name__ == "__main__":
    xlsx = os.getenv("PRODUCTS_XLSX", "./data/products.xlsx")
    seed_products(xlsx)
