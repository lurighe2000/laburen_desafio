# Addons: pgAdmin + Postman

## pgAdmin
- Servicio `pgadmin` en `docker-compose.yml` (sin `version:`).
- URL: http://localhost:5050
- Login: `admin@local` / `admin`
- Conexión precargada: **Laburen Postgres** -> host `db`, puerto `5432`, DB `appdb`, user `appuser`.
- La primera vez te pedirá la password del servidor: `apppass`.

### Levantar pgAdmin
```bash
docker compose up -d pgadmin
# o todo el stack
docker compose up -d
```

## Postman / Newman
- Colección: `tests/Laburen.postman_collection.json`
- Entorno: `tests/Laburen.postman_environment.json` (base_url = http://localhost:8000)

### Correr con Newman (sin instalar Node)
```powershell
# Windows PowerShell
.	estsun_newman.ps1
```
```bash
# macOS/Linux
bash ./tests/run_newman.sh
```

