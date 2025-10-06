# Fase práctica — API + Postgres + agente ejecutable

Este repo contiene:
- **FastAPI** con endpoints `/products`, `/products/:id`, `/carts` (POST), `/carts/:id` (PATCH).
- **PostgreSQL** con 3 tablas: `products`, `carts`, `cart_items`.
- **Seed** desde `api/data/products.xlsx`.
- **Agente** (`scripts/agent.py`) que simula una conversación de compra y usa la API.

## Ejecutar con Docker
```bash
docker compose up --build
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

Para reseedear (cargar productos), entra al contenedor o ejecuta en local:
```bash
docker compose exec api python -m app.seed
```

## Ejecutar sin Docker (local)
1) Levantá Postgres y crea la DB `appdb` y usuario `appuser/apppass` (o ajustá `api/.env`).  
2) Instalá deps en `api/`:
```bash
cd api
pip install -U pip
pip install poetry
poetry install
cp .env.example .env  # editar si es necesario
poetry run uvicorn app.main:app --reload
```
3) Seed de productos:
```bash
poetry run python -m app.seed
```

## Estructura de tablas
- **products**: id (PK), name, description, price, stock
- **carts**: id (PK), created_at, updated_at
- **cart_items**: id (PK), cart_id (FK), product_id (FK), qty

## Endpoints
- `GET /products?q=` — filtra por nombre/descr. (ILIKE)  
- `GET /products/{id}` — detalle (404 si no existe)  
- `POST /carts` — Body: `{ "items":[{"product_id":1,"qty":2}] }` → 201 con carrito creado (y sus items).  
- `PATCH /carts/{id}` — Body: `{ "items":[{"product_id":1,"qty":0}] }` → actualizar cantidades o eliminar si qty=0.

## Semillas (XLSX)
Detected columns in products.xlsx: ['ID', 'TIPO_PRENDA', 'TALLA', 'COLOR', 'CANTIDAD_DISPONIBLE', 'PRECIO_50_U', 'PRECIO_100_U', 'PRECIO_200_U', 'DISPONIBLE', 'CATEGORÍA', 'DESCRIPCIÓN']
First rows sample:
[
  {
    "ID": 1,
    "TIPO_PRENDA": "Pantalón",
    "TALLA": "XXL",
    "COLOR": "Verde",
    "CANTIDAD_DISPONIBLE": 177,
    "PRECIO_50_U": 1058,
    "PRECIO_100_U": 1182,
    "PRECIO_200_U": 462,
    "DISPONIBLE": "Sí",
    "CATEGORÍA": "Deportivo",
    "DESCRIPCIÓN": "Ideal para uso diario."
  },
  {
    "ID": 2,
    "TIPO_PRENDA": "Camiseta",
    "TALLA": "XXL",
    "COLOR": "Blanco",
    "CANTIDAD_DISPONIBLE": 33,
    "PRECIO_50_U": 510,
    "PRECIO_100_U": 975,
    "PRECIO_200_U": 739,
    "DISPONIBLE": "Sí",
    "CATEGORÍA": "Deportivo",
    "DESCRIPCIÓN": "Prenda cómoda y ligera."
  },
  {
    "ID": 3,
    "TIPO_PRENDA": "Camiseta",
    "TALLA": "S",
    "COLOR": "Negro",
    "CANTIDAD_DISPONIBLE": 457,
    "PRECIO_50_U": 1292,
    "PRECIO_100_U": 457,
    "PRECIO_200_U": 873,
    "DISPONIBLE": "Sí",
    "CATEGORÍA": "Casual",
    "DESCRIPCIÓN": "Diseño moderno y elegante."
  }
]

**Mapeo esperado de columnas** (case-insensitive):
- `name`
- `description` (opcional; default vacío)
- `price` (numérico)
- `stock` (entero)

Cualquier columna extra se ignora. Si tu archivo usa otros nombres, editá `app/seed.py`.

## Agente ejecutable
```bash
# con Docker (en otra terminal)
python3 scripts/agent.py --base-url http://localhost:8000
# o:
python3 scripts/agent.py --demo  # usa flujos predefinidos
```
El agente:
- Busca productos (`/products?q=`).
- Crea un carrito con algunos items (`/carts`).
- Actualiza cantidades (`/carts/:id`).
- Muestra el resumen final del carrito.

## Licencia
MIT
