# app/whatsapp_server.py
import os
from flask import Flask, request, jsonify
import requests
from app.agent.shopping_agent import ShoppingAgent
import json

app = Flask(__name__)

# Deben venir por variables de entorno. Fallback SOLO para VERIFY_TOKEN.
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "laburen2025")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")  # ej: "801551269711659"

def send_whatsapp_text(to: str, body: str):
    if not (WHATSAPP_TOKEN and PHONE_NUMBER_ID):
        raise RuntimeError("Faltan WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID en variables de entorno")
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:4000]}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    r.raise_for_status()

@app.route("/wa/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ WEBHOOK_VERIFIED")
        return challenge, 200
    return "error", 403

@app.route("/wa/webhook", methods=["POST"])
def incoming():
    data = request.get_json(force=True, silent=True) or {}
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") == "text":
                        user_number = msg["from"]
                        text = msg["text"]["body"]
                        session_id = f"wa:{user_number}"
                        agent = ShoppingAgent(session_id)
                        resp = agent.handle(text)
                        send_whatsapp_text(user_number, resp)
    except Exception as e:
        print("Webhook error:", e)
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))


# --- healthcheck (Render lo usa para saber si está vivo) ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

# --- logueo claro del POST entrante ---
@app.route("/wa/webhook", methods=["POST"])
def incoming():
    data = request.get_json(force=True, silent=True) or {}
    print("\n=== WEBHOOK IN ===")
    try:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(str(data))
    print("=== /WEBHOOK IN ===\n")
    # ... (tu código de parseo/respuesta como ya lo tenés)
    try:
        # (tu lógica actual)
        ...
    except Exception as e:
        print("Webhook error:", e)
    return jsonify(status="ok"), 200
