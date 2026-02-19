# 🐳 Production-Ready Containerized Web Application

An **End-to-End Production project** built with **FastAPI**, **PostgreSQL**, **Redis**, and **Nginx reverse proxy**, orchestrated with Docker Compose. This project combines everything learned throughout the Docker practice repo into one fully async, production-grade application.

---

## 📁 Project Structure

```
production-webapp/
├── app/
│   ├── main.py               # FastAPI application (fully async)
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Multistage Python image
├── default.conf              # Nginx reverse proxy + upstream config
├── .env                      # Environment variables for FastAPI
└── compose.yml               # Multi-container orchestration
```

---

## 🚀 App Overview

A fully async FastAPI application with real database and caching integration:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check — confirms app is running |
| POST | `/users` | Create a new user in PostgreSQL |
| GET | `/users` | Get all users (Redis cached for 60s) |
| GET | `/redis` | Test Redis async connection |
| GET | `/postgres` | Test PostgreSQL connection + version |

### Caching Strategy
- `GET /users` checks Redis first — if cached, returns instantly without hitting PostgreSQL
- `POST /users` invalidates the `users_cache` key so the next `GET /users` fetches fresh data
- Cache TTL is **60 seconds**

---

## 🏗️ Architecture

```
                            ┌─────────────────────────────────────────────────────┐
                            │                  nginx-fastapi network               │
                            │                                                      │
Host:4000 ──────────────▶  │  nginx (port 80)                                     │
                            │      │                                               │
                            │      │ proxy_pass http://fastapi_app                │
                            │      ▼                                               │
                            │  fastapi (port 6000)                                 │
                            └──────────────┬──────────────────────────────────────┘
                                           │
                  ┌────────────────────────┼────────────────────────┐
                  │                        │                         │
   ┌──────────────▼──────────────┐  ┌─────▼───────────────────────┐│
   │     fastapi-postgress        │  │      fastapi-redis           ││
   │                              │  │                              ││
   │  postgres:5432               │  │  redis:6379                  ││
   │  (postgres_data volume)      │  │  (redis_data volume)         ││
   └──────────────────────────────┘  └──────────────────────────────┘
```

### Three Networks — Why?

| Network | Members | Purpose |
|---------|---------|---------|
| `nginx-fastapi` | nginx, fastapi | Nginx forwards HTTP traffic to FastAPI |
| `fastapi-postgress` | fastapi, postgres | FastAPI reads/writes to PostgreSQL |
| `fastapi-redis` | fastapi, redis | FastAPI reads/writes to Redis cache |

Each service is isolated to **only the networks it needs**:
- Nginx **cannot** reach PostgreSQL or Redis directly
- PostgreSQL and Redis **cannot** reach each other
- Only FastAPI sits in the middle as the bridge between all layers

---

## 🐋 Docker Compose Breakdown

### `nginx`
- Official `nginx:latest` image
- Exposed on host port `4000`, internal port `80`
- Uses a **bind mount** for `default.conf` — no need to rebuild the image to change Nginx config
- Depends on `fastapi`
- Connected to `nginx-fastapi` network only

### `fastapi`
- Built from `app/Dockerfile`
- **Not exposed to host** — all traffic goes through Nginx
- Loads environment variables from `.env` via `env_file`
- Connected to all three networks (nginx-fastapi, fastapi-postgress, fastapi-redis)
- Depends on `postgres` and `redis`

### `postgres`
- Official `postgres:16` image
- **Internal only** via `expose: 5432`
- Database, user, and password set via environment variables (PostgreSQL supports this natively)
- Data persisted in `postgres_data` volume

### `redis`
- Official `redis:6.2-alpine` image
- **Internal only** via `expose: 6379`
- Data persisted in `redis_data` volume
- Alpine-based for minimal image size

---

## 🔁 Nginx as Reverse Proxy — `default.conf` Explained

```nginx
# Define the upstream group (load balancer ready)
upstream fastapi_app {
    server fastapi:6000;   # Docker DNS resolves "fastapi" to container IP
    # server fastapi:5001; # Uncomment to add a second instance for load balancing
}

server {
    listen 80;

    location / {
        proxy_pass http://fastapi_app;           # forward all requests to FastAPI
        proxy_set_header Host $host;             # pass original host header
        proxy_set_header X-Real-IP $remote_addr; # pass real client IP to FastAPI
    }
}
```

### What Nginx provides here:
- **Reverse proxy** — hides FastAPI from the public, single entry point
- **Load balancing** — just add more `server fastapi:port` lines to the upstream block
- **SSL termination** — can add HTTPS here without touching the FastAPI app
- **Centralized logging** — all traffic logs in one place
- **Static file serving** — can serve static files directly without hitting FastAPI

### Bind Mount vs COPY
```yaml
volumes:
  - ./default.conf:/etc/nginx/conf.d/default.conf  # bind mount
```
The Nginx config is **bind mounted** instead of baked into the image with `COPY`. This means you can update `default.conf` and restart Nginx **without rebuilding the image** — much faster for iteration.

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Install dependencies into a venv
FROM python:3.10 AS build
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Slim runtime image
FROM python:3.10-slim
COPY --from=build /opt/venv /opt/venv
WORKDIR /app
COPY . .
ENV PATH="$PATH:/opt/venv/bin"
EXPOSE 6000

# Run with Uvicorn — ASGI server for async FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000", "--loop", "asyncio"]
```

> FastAPI is an **ASGI** framework — it runs with **Uvicorn**, not Gunicorn. The `--loop asyncio` flag explicitly sets the async event loop.

---

## ⚙️ Environment Variables — `.env`

```env
DB_HOST=postgres       # must match the postgres service name in compose
DB_PORT=5432           # internal Docker network port, NOT host-mapped port
DB_USER=youssef
DB_PASSWORD=123
DB_NAME=psql_db

REDIS_HOST=redis       # must match the redis service name in compose
REDIS_PORT=6379
```

The `.env` file is loaded into the `fastapi` container via:
```yaml
env_file:
  - .env
```

> ⚠️ Add `.env` to `.gitignore` — never commit real credentials to source control.

### Why service names as hostnames?
Docker Compose's built-in DNS resolves service names to container IPs automatically. `DB_HOST=postgres` means "connect to the container named `postgres` on the internal network" — Docker figures out the IP.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Async web framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy` | ORM for database models |
| `asyncpg` | Async PostgreSQL driver |
| `redis[asyncio]` | Async Redis client |
| `python-dotenv` | Load `.env` file |
| `psycopg2-binary` | Sync PostgreSQL driver (fallback) |

---

## 💾 Volumes

| Volume | Mounted At | Purpose |
|--------|-----------|---------|
| `postgres_data` | `/var/lib/postgresql/data` | Persists PostgreSQL databases |
| `redis_data` | `/data` | Persists Redis data |

---

## 🔒 Security Scanning with Trivy

All images should be scanned with **Trivy** before pushing to production.

```bash
# Scan the FastAPI image
docker build -t production-fastapi ./app
trivy image production-fastapi

# Scan pulled images
trivy image postgres:16
trivy image redis:6.2-alpine
trivy image nginx:latest

# Filter by severity
trivy image --severity CRITICAL,HIGH production-fastapi

# Save report
trivy image production-fastapi > trivy-report.txt
```

> Alpine-based images like `redis:6.2-alpine` typically have significantly fewer vulnerabilities than Debian/Ubuntu-based equivalents.

---

## 🛠️ Build & Run

### Start all services

```bash
docker-compose -f compose.yml up --build
```

### Run in detached mode

```bash
docker-compose -f compose.yml up --build -d
```

### Test the endpoints

```bash
# Health check
curl http://localhost:4000/

# Test Redis
curl http://localhost:4000/redis

# Test PostgreSQL
curl http://localhost:4000/postgres

# Create a user
curl -X POST http://localhost:4000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Youssef", "email": "youssef@example.com"}'

# Get all users (first call hits DB, subsequent calls hit Redis cache)
curl http://localhost:4000/users
```

### Stop containers

```bash
docker-compose -f compose.yml down
```

### Stop and remove volumes (wipes all data)

```bash
docker-compose -f compose.yml down -v
```

---

## 💡 Key Concepts Practiced

- ✅ Full production stack — Nginx + FastAPI + PostgreSQL + Redis
- ✅ Three isolated networks for strict service-level security
- ✅ Nginx as reverse proxy with upstream load balancing config
- ✅ Bind mount for Nginx config — no rebuild needed on config change
- ✅ Fully async FastAPI with SQLAlchemy async engine + asyncpg
- ✅ Redis caching with cache invalidation strategy
- ✅ Auto table creation on startup via SQLAlchemy `create_all`
- ✅ `.env` file loaded via `env_file` in Compose
- ✅ Docker internal DNS — service names as hostnames
- ✅ `expose` for internal-only services (postgres, redis)
- ✅ Multistage build with venv for slim Python image
- ✅ Alpine-based Redis image for reduced attack surface
- ✅ Security scanning with Trivy
- ✅ Named volumes for data persistence across restarts