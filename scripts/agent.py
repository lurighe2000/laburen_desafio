import argparse, requests, time, sys

def log(msg): print(f"[agent] {msg}", flush=True)

def find_products(base_url, q):
    r = requests.get(f"{base_url}/products", params={"q": q}, timeout=10)
    r.raise_for_status()
    return r.json()

def create_cart(base_url, items):
    r = requests.post(f"{base_url}/carts", json={"items": items}, timeout=10)
    r.raise_for_status()
    return r.json()

def patch_cart(base_url, cart_id, items):
    r = requests.patch(f"{base_url}/carts/{cart_id}", json={"items": items}, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--demo", action="store_true", help="ejecuta flujo predefinido")
    args = parser.parse_args()

    base = args.base_url
    log(f"Usando API en {base}")

    if args.demo:
        # Buscar algo genérico
        results = find_products(base, q="")
        if not results:
            log("No hay productos. Corre el seed primero.")
            sys.exit(1)

        # Tomar los primeros 2
        picks = results[:2]
        log(f"Encontré {len(results)} productos. Voy a crear un carrito con los 2 primeros.")
        items = [{"product_id": p["id"], "qty": 1} for p in picks]
        cart = create_cart(base, items)
        log(f"Carrito creado: #{cart['id']} con {len(cart['items'])} items.")

        # Aumentar cantidad del primer item
        first_pid = picks[0]["id"]
        cart = patch_cart(base, cart["id"], [{"product_id": first_pid, "qty": 3}])
        log("Actualicé la cantidad del primer item a 3.")

        # Eliminar el segundo
        second_pid = picks[1]["id"]
        cart = patch_cart(base, cart["id"], [{"product_id": second_pid, "qty": 0}])
        log("Eliminé el segundo item del carrito.")

        # Resumen final
        total = 0.0
        for it in cart["items"]:
            total += it["qty"] * it["product"]["price"]
        log(f"Resumen carrito #{cart['id']}: {len(cart['items'])} items | Total: ${total:.2f}")
        for it in cart["items"]:
            p = it["product"]
            log(f"- {p['name']} x{it['qty']} @ ${p['price']:.2f}")

    else:
        log("Modo interactivo. Escribí un término de búsqueda (o vacío para listar). Ctrl+C para salir.")
        while True:
            try:
                q = input("Buscar: ").strip()
                prods = find_products(base, q)
                for p in prods[:10]:
                    print(f"{p['id']:>3} | {p['name'][:40]:40} | ${p['price']:.2f} | stock:{p['stock']}")
                if not prods:
                    continue
                sel = input("Elegí IDs separados por coma (ej: 1,2): ").strip()
                ids = [int(x) for x in sel.split(",") if x.strip().isdigit()]
                items = [{"product_id": pid, "qty": 1} for pid in ids]
                cart = create_cart(base, items)
                print(f"Carrito #{cart['id']} creado.")
                break
            except KeyboardInterrupt:
                print("\nSaliendo...")
                return

if __name__ == "__main__":
    main()
