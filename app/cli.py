# app/cli.py
import sys
from app.agent.shopping_agent import ShoppingAgent


def main():
    session = "local-cli"
    agent = ShoppingAgent(session_id=session)
    print("Agente de compras listo. Escribí 'salir' para terminar.")
    while True:
        try:
            txt = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChau!")
            break
        if txt.lower() in ("salir", "exit", "quit"):
            print("Chau!")
            break
        resp = agent.handle(txt)
        print(resp)

if __name__ == "__main__":
    main()
