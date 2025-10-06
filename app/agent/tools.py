# app/agent/tools.py
import os
import requests
from typing import Any, Dict, List, Optional, Tuple

API_BASE = os.environ.get("API_BASE", "http://api:8000")  # en docker compose, servicio "api"
# Para correr fuera de docker: export API_BASE=http://localhost:8000

class ApiError(Exception):
    pass

def _handle_response(r: requests.Response) -> Any:
    if r.status_code in (200, 201):
        return r.json()
    elif r.status_code == 404:
        raise ApiError("404")
    else:
        raise ApiError(f"HTTP {r.status_code}: {r.text}")

def search_products(q: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {"q": q} if q else {}
    r = requests.get(f"{API_BASE}/products", params=params, timeout=10)
    return _handle_response(r)

def get_product(pid: int) -> Dict[str, Any]:
    r = requests.get(f"{API_BASE}/products/{pid}", timeout=10)
    return _handle_response(r)

def create_cart(items: List[Dict[str, int]]) -> Dict[str, Any]:
    # items = [{ "product_id": int, "qty": int }]
    r = requests.post(f"{API_BASE}/carts", json={"items": items}, timeout=10)
    return _handle_response(r)

def patch_cart(cart_id: int, items: List[Dict[str, int]]) -> Dict[str, Any]:
    r = requests.patch(f"{API_BASE}/carts/{cart_id}", json={"items": items}, timeout=10)
    return _handle_response(r)