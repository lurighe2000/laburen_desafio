# Laburen — Agente IA + API PostgreSQL (Fase 3)

Proyecto de agente (WhatsApp) que **consume una API en Node/Express + PostgreSQL**. Este README deja listo el **entregable de la Fase 3** con estructura de carpetas, pasos de despliegue y verificación.

---

## 1) Entregables (checklist)

* [x] **Repositorio GitHub** con código y README completo.
* [x] **Carpeta `/docs`** con diagramas y documento conceptual.
* [x] **Número del agente en WhatsApp** consumiendo la API (evidencias: capturas/video).

---

## 2) Estructura del repositorio

```
laburen_api_postgres_agent/
├─ src/
│  ├─ api/
│  │  ├─ index.ts               # bootstrap Express
│  │  ├─ routes/
│  │  │  └─ v1.ts               # endpoints REST
│  │  ├─ controllers/
│  │  │  └─ items.controller.ts
│  │  ├─ services/
│  │  │  └─ items.service.ts
│  │  ├─ db/
│  │  │  ├─ client.ts           # pool pg
│  │  │  └─ migrations/         # SQL / ORM (ej. Prisma/Knex)
│  │  └─ middlewares/
│  ├─ agent/
│  │  ├─ whatsapp.ts            # integración WA Cloud API / Baileys / etc.
│  │  └─ handlers.ts            # intents y flujos
│  └─ config/
│     └─ env.ts                 # lectura de .env
│
├─ docs/
│  ├─ diagrama_flujo_agente.png
│  ├─ arquitectura_api.png
│  └─ documento_conceptual.pdf
│
├─ .env.example
├─ package.json
├─ tsconfig.json
├─ README.md
└─ LICENSE (opcional)
```

> **Nota**: Si tu proyecto usa JavaScript puro, reemplazá `.ts` por `.js` y eliminá `tsconfig.json`.

---

## 3) Variables de entorno (`.env`)

Copiá `.env.example` a `.env` y completá tus valores reales.

```ini
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/laburen

# Server
PORT=3000
NODE_ENV=production

# WhatsApp (si usás Cloud API)
WA_PHONE_ID="
WA_ACCESS_TOKEN="
WA_TO_SANDBOX=""

# Otros
LOG_LEVEL=info
```

---

## 4) Instalación y ejecución local

```bash
# 1) Instalar dependencias
npm i

# 2) Compilar (si usás TS) y correr
npm run build && npm start
# o en dev
npm run dev
```

### Migraciones/DB

* **ORM** (Prisma/Knex): agregá scripts `npm run migrate`.
* **SQL plano**: incluí archivos en `src/api/db/migrations/` y un script de ejecución.

---

## 5) API — endpoints mínimos (ejemplo v1)

```
GET  /api/v1/health         -> { status: "ok" }
GET  /api/v1/items          -> lista de items
POST /api/v1/items          -> crea item
```

Dejá ejemplos en el README o en **docs/api.http** (para VSCode REST Client) o **docs/postman_collection.json**.

---

## 6) Agente de WhatsApp — flujo mínimo

1. Usuario envía mensaje: "hola".
2. Agente responde saludo y **consulta a la API** `GET /api/v1/items`.
3. Devuelve respuesta formateada al usuario (y maneja errores).

### Evidencia de consumo real

* Captura del mensaje del usuario.
* Captura de la respuesta del bot con **data real de la API**.
* (Opcional) Mini video (10–20 s) mostrando la interacción.

---

## 7) Despliegue (ejemplo)

* **API**: Render, Railway, Fly.io, Vercel (con serverless) o VPS propio.
* **DB**: PostgreSQL gestionado (Railway/Neon/Supabase) o tu VPS.
* **Agente**:

  * *WhatsApp Cloud API*: Node server + webhook público (ej. Render) y verificación de tokens.
  * *Baileys/MD*: proceso Node vivo con número propio.

> Asegurate de exponer `GET /api/v1/health` y probarlo desde internet antes de enlazar el bot.

---

## 8) Comandos Git para la entrega

```bash
# configurar remoto (si aún no lo hiciste)
git remote -v
# si ves https://github.com/<tu-usuario>/<tu-repo>.git corregí con:
git remote set-url origin https://github.com/<tu-usuario>/<repo-real>.git

# agregar todo y commitear
git add .
git commit -m "Fase 3: estructura final + README + docs"

# push a main
git push -u origin main

# crear tag de entrega (opcional)
git tag -a v3.0.0 -m "Entrega Fase 3"
git push origin v3.0.0
```

---

## 9) Qué enviar al evaluador

* **Enlace del repositorio** (público o con acceso).
* **Carpeta `/docs`** con diagramas + documento conceptual.
* **Número de WhatsApp del agente** y **evidencias** (capturas/video corto).
* (Opcional) URL pública del **endpoint `GET /api/v1/health`**.

### Plantilla breve para el mensaje (WhatsApp/Email)

```
Hola, comparto entregables Fase 3:
• Repo: https://github.com/<usuario>/<repo>
• Docs: en /docs (diagramas + conceptual)
• Health API: https://<mi-api>/api/v1/health
• WhatsApp del agente: +54 9 xxx xxx xxxx
Adjunto capturas del bot consumiendo la API. ¡Gracias!
```

---

## 10) Documentación conceptual (resumen)

Incluí en `docs/documento_conceptual.pdf`:

* **Objetivo** del agente y casos de uso.
* **Arquitectura** (diagrama alto nivel: usuario → agente → API → DB).
* **Modelo de datos** (ER o esquema tablas principales).
* **Flujos** (mensajería y manejo de errores/timeouts).
* **Seguridad** (tokens, validación, CORS, rate limiting) y **logs/observabilidad**.

---

## 11) Troubleshooting rápido

* **404/timeout API**: revisá `PORT`, `CORS` y URL pública.
* **DB rechaza conexión**: whitelist de IPs/SSL, credenciales `.env`.
* **WhatsApp** no responde: chequeá **webhook verificado**, **token vigente**, logs del server.

---

## 12) Licencia

* Agregá `LICENSE` si tu repo será público (MIT recomendado).

---

## 13) Créditos

* Equipo Laburen — Fase 3.
