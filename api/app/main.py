from fastapi import FastAPI
from .db import Base, engine
from .routers import products, carts

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Laburen API — Fase práctica", version="0.1.0")

app.include_router(products.router)
app.include_router(carts.router)

@app.get("/health")
def health():
    return {"status": "ok"}
