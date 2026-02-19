

# 🐳 Docker Compose — Python + Redis + MySQL

A **Flask** web application connected to **Redis** (caching) and **MySQL** (persistent storage), orchestrated with **Docker Compose**. Demonstrates how multiple containers communicate over a shared network using Docker's internal DNS.

---

## 📁 Project Structure

```
python-redis-mysql/
├── app/
│   └── app.py              # Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Multistage Python image
└── docker-compose.yml      # Multi-container orchestration
```

---



## Features

- Python Flask web application
- Redis for caching
- MySQL for persistent storage
- Docker containerization


## 🚀 App Overview

A Flask API with 3 endpoints to verify connectivity with each service:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/redis` | Sets & gets a test key from Redis |
| GET | `/mysql` | Runs a test query against MySQL |

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │         app_network              │
                    │                                  │
Host:9002 ──────▶  │  python-app:6000                 │
                    │       │           │              │
                    │       ▼           ▼              │
                    │  redis:6379   mysql:3306         │
                    │       │           │              │
                    │  redis_data   mysql_data         │
                    │  (volume)     (volume)           │
                    └─────────────────────────────────┘
```

- Only `python-app` is exposed to the host (`9002:6000`)
- Redis and MySQL are **internal only** — reachable by service name, not exposed outside
- All three containers share `app_network`

---

## 🐋 Docker Compose Breakdown

### Services

#### `python-app`
- Built from the local `Dockerfile`
- Exposed on host port `9002`, internal port `6000`
- Connects to Redis and MySQL using **service names as hostnames**
- Waits for `redis` and `mysql` to start via `depends_on`

#### `redis`
- Official `redis:6.2-alpine` image
- **Not exposed to host** — only accessible inside `app_network`
- Data persisted in `redis_data` named volume

#### `mysql`
- Official `mysql:8.0` image
- **Not exposed to host** — only accessible inside `app_network`
- Uses `mysql_native_password` authentication plugin for compatibility
- Data persisted in `mysql_data` named volume

---

## 🌐 Docker Compose DNS — How Containers Find Each Other

This is one of the most important concepts in this project:

```yaml
environment:
  - REDIS_HOST=redis    # "redis" resolves to the redis container's IP
  - MYSQL_HOST=mysql    # "mysql" resolves to the mysql container's IP
```

Docker Compose has a **built-in DNS resolver**. Each service name acts as a hostname that automatically resolves to that container's internal IP address. This means:

- You **never hardcode IPs** — they change every time containers restart
- The app just uses `redis` and `mysql` as hostnames and Docker handles the rest
- Ports used here are the **container's internal ports** (`6379`, `3306`), NOT the host-mapped ports

> ⚠️ If you mapped Redis to `9001:6379` on the host, the app still connects on port `6379` — because inside the network, Redis listens on `6379`. The `9001` mapping is only for accessing Redis from your machine.

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Install dependencies into a venv
FROM python:3.9-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir gunicorn

# Stage 2: Slim runtime image
FROM python:3.9-slim
COPY --from=deps /opt/venv /opt/venv
WORKDIR /app
COPY . .
ENV PATH="$PATH:/opt/venv/bin"
EXPOSE 6000

# Run with Gunicorn — 3 workers, bound to all interfaces
# app.app:app → app/ folder → app.py file → app Flask instance
CMD ["gunicorn", "app.app:app", "--bind", "0.0.0.0:6000", "--workers", "3"]
```

> Note the `app.app:app` in the CMD — this means: `app/` package → `app.py` module → `app` Flask instance.

---

## ⚙️ Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `REDIS_HOST` | `redis` | Redis service name (resolves via Docker DNS) |
| `REDIS_PORT` | `6379` | Redis internal port |
| `MYSQL_HOST` | `mysql` | MySQL service name (resolves via Docker DNS) |
| `MYSQL_DATABASE` | `mydb` | Database name |
| `MYSQL_USER` | `youssef` | MySQL user |
| `MYSQL_PASSWORD` | `123` | MySQL user password |
| `MYSQL_ROOT_PASSWORD` | `password` | MySQL root password (set on mysql service) |

> ⚠️ **Never commit real passwords to source control.** Use a `.env` file and add it to `.gitignore` for production setups.

---

## 💾 Volumes

| Volume | Mounted At | Purpose |
|--------|-----------|---------|
| `redis_data` | `/data` | Persists Redis data across container restarts |
| `mysql_data` | `/var/lib/mysql` | Persists MySQL databases across container restarts |

Without volumes, all data is lost when containers are removed.

---

## 🛠️ Build & Run

### Start all services

```bash
docker-compose up --build
```

### Run in detached mode

```bash
docker-compose up --build -d
```

### Test the endpoints

```bash
# Welcome message
curl http://localhost:9002

# Test Redis
curl http://localhost:9002/redis

# Test MySQL
curl http://localhost:9002/mysql
```

### Stop containers

```bash
docker-compose down
```

### Stop and remove volumes (wipes all data)

```bash
docker-compose down -v
```

---

## 💡 Key Concepts Practiced

- ✅ Docker Compose multi-container orchestration
- ✅ Docker internal DNS — service name as hostname
- ✅ Named volumes for data persistence (Redis + MySQL)
- ✅ Custom bridge network (`app_network`) for container isolation
- ✅ Only exposing necessary ports to the host
- ✅ `depends_on` for service startup ordering
- ✅ Environment variables for service configuration
- ✅ Multistage build with venv for the Python app
- ✅ Gunicorn as production WSGI server with multiple workers