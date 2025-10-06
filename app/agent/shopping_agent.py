# app/agent/shopping_agent.py
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple
from .tools import search_products, get_product, create_cart, patch_cart, ApiError

# Memoria breve por sesión (ej: filtros), y cart_id por conversación.
# En prod, sustituir por Redis/DB. Acá mantenemos en memoria.
SESSION_STATE: Dict[str, Dict[str, Any]] = {}

def _state(session_id: str) -> Dict[str, Any]:
    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {"cart_id": None, "filters": {}}
    return SESSION_STATE[session_id]

class ShoppingAgent:
    """
    Agente conversacional de compras (ES).
    Intenciones: buscar, detalle, agregar/quitar/cambiar qty, ver carrito/total, ayuda.
    - Un cart_id por conversación (se crea si no existe al agregar).
    - Respuestas concisas y confirmando cambios.
    - Manejo de errores: 404 producto, qty inválida, carrito vacío.
    - Memoria breve: recuerda filtros (p.ej., color/talle) en la sesión.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = _state(session_id)

    # ---------- NLU súper ligera (regex + heurísticas) ----------
    def parse(self, text: str) -> Dict[str, Any]:
        t = text.lower().strip()

        # ayuda
        if any(k in t for k in ["ayuda", "qué sabés hacer", "como uso", "help"]):
            return {"intent": "help"}

        # ver carrito / total
        if re.search(r"\b(carrito|total|ver carrito|mostrar carrito)\b", t):
            return {"intent": "show_cart"}

        # detalle por id
        m = re.search(r"(detalle|info|información)\s+(id|producto)\s*(\d+)", t)
        if m:
            return {"intent": "detail", "product_id": int(m.group(3))}

        # agregar X unidades de producto Y (por id)
        m = re.search(r"(agrega|agregá|añade|sumar|agregar)\s*(\d+)\s*(?:x|unidades?|u\.?)?\s*(?:del\s*)?(?:producto\s*)?(\d+)", t)
        if m:
            return {"intent": "add", "qty": int(m.group(2)), "product_id": int(m.group(3))}

        # agregar por id simple: "agregar producto 5", qty=1
        m = re.search(r"(agrega|agregá|agregar|sumar).*(producto\s*)(\d+)", t)
        if m:
            return {"intent": "add", "qty": 1, "product_id": int(m.group(3))}

        # quitar/cambiar qty
        # "quitar 1 del producto 5" => qty negativa
        m = re.search(r"(quita|quitar|remueve|remover|saca|sacar)\s*(\d+)\s*(?:x|unidades?)?\s*(?:del\s*)?(?:producto\s*)?(\d+)", t)
        if m:
            return {"intent": "add", "qty": -int(m.group(2)), "product_id": int(m.group(3))}

        # "cambiar producto 5 a 3" => set qty 3
        m = re.search(r"(cambia|cambiar|setea|poner|deja)\s*(?:el\s*)?(?:producto\s*)?(\d+)\s*(?:a|en)\s*(\d+)", t)
        if m:
            return {"intent": "set_qty", "product_id": int(m.group(2)), "qty": int(m.group(3))}

        # quitar por id completo: "quitar producto 5" => qty 0
        m = re.search(r"(quita|quitar|remueve|remover|saca|sacar).*(producto\s*)(\d+)", t)
        if m:
            return {"intent": "set_qty", "product_id": int(m.group(3)), "qty": 0}

        # buscar (por texto)
        # guarda filtros recordados (color/talle) si aparecen
        filters = {}
        m_color = re.search(r"\b(color|colores?)\s*:\s*([a-záéíóúñ]+)", t)
        if m_color:
            filters["color"] = m_color.group(2)
        m_talle = re.search(r"\b(talle|tamaño|size)\s*:\s*([a-z0-9\-]+)", t)
        if m_talle:
            filters["talle"] = m_talle.group(2)

        # “busca medias negras”, “mostrá productos”, “tenés zoquetes?”
        if any(k in t for k in ["busca", "buscá", "buscar", "productos", "tenes", "tenés", "mostra", "mostrá", "mostrame"]):
            q = re.sub(r"(busca|buscá|buscar|mostra|mostrá|mostrame|productos|tenes|tenés)", "", t).strip()
            q = re.sub(r"(color\s*:\s*\w+|talle\s*:\s*\w+)", "", q).strip()
            return {"intent": "search", "q": q if q else None, "filters": filters or None}

        # fallback a ayuda
        return {"intent": "help"}

    # ---------- Lógica por intención ----------
    def handle(self, text: str) -> str:
        intent = self.parse(text)

        try:
            if intent["intent"] == "help":
                return (
                    "Puedo buscar productos, ver detalle por id, y gestionar tu carrito:\n"
                    "• Buscar: “buscá medias negras”, “mostrá productos color:negro talle:M”.\n"
                    "• Detalle: “detalle producto 5”.\n"
                    "• Agregar: “agregá 2 del producto 5”. Quitar: “quitar 1 del producto 5”.\n"
                    "• Cambiar cantidad: “cambiar producto 5 a 3”.\n"
                    "• Ver carrito/total: “ver carrito”."
                )

            if intent["intent"] == "search":
                if intent.get("filters"):
                    self.state["filters"].update(intent["filters"])
                q = intent.get("q")
                # Puedes enriquecer q con filtros recordados (opcional)
                filter_hint = ""
                if self.state["filters"]:
                    # Nota: tu API actual no acepta color/talle, lo dejamos como memoria conversacional
                    filter_hint = " (recordando filtros de sesión)"
                products = search_products(q)
                if not products:
                    return "No encontré productos con ese criterio."
                top = products[:5]
                lines = [f"{p['id']}. {p['name']} — ${p['price']} (stock: {p['stock']})" for p in top]
                more = "" if len(products) <= 5 else f"\n…y {len(products)-5} más. Refiná tu búsqueda.{filter_hint}"
                return "Productos:\n" + "\n".join(lines) + more

            if intent["intent"] == "detail":
                pid = intent["product_id"]
                p = get_product(pid)
                return f"{p['id']}. {p['name']}\n${p['price']} | stock: {p['stock']}\n{p.get('description','')}".strip()

            if intent["intent"] in ("add", "set_qty"):
                pid = intent["product_id"]
                # valida existencia
                _ = get_product(pid)

                # aseguramos cart
                if not self.state["cart_id"]:
                    cart = create_cart(items=[])
                    self.state["cart_id"] = cart["id"]

                # resolvemos cantidades
                if intent["intent"] == "add":
                    qty_change = intent["qty"]
                    # para add con qty negativa -> suma con signo
                    payload_items = [{"product_id": pid, "qty": qty_change}]
                else:
                    # set_qty a cantidad específica
                    new_qty = intent["qty"]
                    payload_items = [{"product_id": pid, "qty": new_qty}]  # qty=0 elimina

                cart = patch_cart(self.state["cart_id"], payload_items)
                # formateo de total
                total = sum(ci["qty"] * ci["product"]["price"] for ci in cart.get("items", []))
                # mensaje conciso y confirmación
                if intent["intent"] == "add":
                    verb = "Agregué" if payload_items[0]["qty"] > 0 else "Quité"
                    qty_abs = abs(payload_items[0]["qty"])
                    return f"{verb} producto {pid} x{qty_abs}. Total: ${total}."
                else:
                    qv = payload_items[0]["qty"]
                    if qv == 0:
                        return f"Eliminé producto {pid}. Total: ${total}."
                    else:
                        return f"Dejé producto {pid} en {qv}u. Total: ${total}."

            if intent["intent"] == "show_cart":
                if not self.state["cart_id"]:
                    return "Tu carrito está vacío."
                try:
                    cart = patch_cart(self.state["cart_id"], [])  # no-op para obtener estado actual
                except ApiError as e:
                    # Si el carrito no existe ya, reseteamos
                    self.state["cart_id"] = None
                    return "Tu carrito está vacío."
                items = cart.get("items", [])
                if not items:
                    return "Tu carrito está vacío."
                lines = []
                total = 0
                for it in items:
                    pid = it["product"]["id"]
                    name = it["product"]["name"]
                    qty = it["qty"]
                    price = it["product"]["price"]
                    subtotal = qty * price
                    total += subtotal
                    lines.append(f"- {pid} {name} x{qty} = ${subtotal}")
                lines.append(f"Total: ${total}")
                return "\n".join(lines)

            # fallback
            return "No entendí. Escribí “ayuda” para ver ejemplos."

        except ApiError as e:
            if str(e) == "404":
                return "No encuentro ese producto (404)."
            return f"Ocurrió un error con la API. {e}"