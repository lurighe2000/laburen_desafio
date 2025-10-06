# tests/test_agent.py
import pytest
import requests
from requests_mock import Mocker
from app.agent.shopping_agent import ShoppingAgent
import os
from uuid import uuid4


API_BASE = os.environ.get("API_BASE", "http://api:8000")

def mock_products():
    return [
        {"id": 1, "name": "Media negra M", "description": "Cómoda", "price": 1000, "stock": 50},
        {"id": 2, "name": "Media blanca L", "description": "Clásica", "price": 1100, "stock": 30},
        {"id": 3, "name": "Zoquete azul S", "description": "Deportivo", "price": 900, "stock": 20},
    ]

def mock_cart(cart_id=10, items=None):
    items = items or []
    return {"id": cart_id, "items": items}

@pytest.fixture
def agent():
    return ShoppingAgent(session_id="t1")

def test_search_200(agent):
    with Mocker() as m:
        m.get(f"{API_BASE}/products", json=mock_products(), status_code=200)
        resp = agent.handle("Buscá medias")
        assert "Productos:" in resp
        assert "1. Media negra M" in resp

def test_detail_200(agent):
    with Mocker() as m:
        p = mock_products()[0]
        m.get(f"{API_BASE}/products/{p['id']}", json=p, status_code=200)
        resp = agent.handle("Detalle producto 1")
        assert "Media negra M" in resp

def test_detail_404(agent):
    with Mocker() as m:
        m.get(f"{API_BASE}/products/999", json={"detail": "Not found"}, status_code=404)
        resp = agent.handle("Detalle producto 999")
        assert "No encuentro ese producto (404)" in resp

def test_add_creates_cart_201(agent):
    with Mocker() as m:
        p = mock_products()[0]
        m.get(f"{API_BASE}/products/{p['id']}", json=p, status_code=200)
        m.post(f"{API_BASE}/carts", json=mock_cart(cart_id=77), status_code=201)
        # patch devuelve carrito con items
        m.patch(f"{API_BASE}/carts/77", json=mock_cart(77, items=[{"product": p, "qty": 2}]), status_code=200)

        resp = agent.handle("Agregá 2 del producto 1")
        assert "Agregué producto 1 x2" in resp
        assert "Total: $2000" in resp

def test_set_qty_200(agent):
    with Mocker() as m:
        p = mock_products()[1]
        # existencia del producto
        m.get(f"{API_BASE}/products/{p['id']}", json=p, status_code=200)
        # carrito ya existe
        m.post(f"{API_BASE}/carts", json=mock_cart(88), status_code=201)
        m.patch(f"{API_BASE}/carts/88", json=mock_cart(88, items=[{"product": p, "qty": 3}]), status_code=200)

        # primera acción creará cart
        _ = agent.handle("agregar producto 2")
        # ahora setear qty
        m.patch(f"{API_BASE}/carts/88", json=mock_cart(88, items=[{"product": p, "qty": 5}]), status_code=200)
        resp = agent.handle("cambiar producto 2 a 5")
        assert "Dejé producto 2 en 5u" in resp
        assert "Total: $5500" in resp

def test_show_cart_empty(agent):
    # sin cart creado
    resp = agent.handle("ver carrito")
    assert "vacío" in resp

def test_remove_to_zero(agent):
    with Mocker() as m:
        p = mock_products()[2]
        m.get(f"{API_BASE}/products/{p['id']}", json=p, status_code=200)
        m.post(f"{API_BASE}/carts", json=mock_cart(90), status_code=201)
        # Agregar 1
        m.patch(f"{API_BASE}/carts/90", json=mock_cart(90, items=[{"product": p, "qty": 1}]), status_code=200)
        _ = agent.handle("agregar producto 3")
        # Eliminar (qty=0)
        m.patch(f"{API_BASE}/carts/90", json=mock_cart(90, items=[]), status_code=200)
        resp = agent.handle("quitar producto 3")
        assert "Eliminé producto 3" in resp
        assert "Total: $0" in resp

@pytest.fixture
def agent():
    # session_id único por test
    return ShoppingAgent(session_id=f"t-{uuid4()}")