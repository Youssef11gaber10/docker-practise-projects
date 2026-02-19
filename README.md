# 🐳 Docker Practice

A hands-on Docker learning repository covering everything from containerizing single applications to orchestrating multi-container production-grade stacks with Docker Compose.

The repo is split into two main sections: **dockerize-applications** (single container projects) and **docker-compose** (multi-container projects).

---

## 📁 Repository Structure

```
docker-practice/
├── dockerize-applications/
│   ├── nodejs/                # Node.js Express app — multistage build
│   ├── node-TS/               # TypeScript Node.js app — multistage build
│   ├── python asgi/           # Custom ASGI framework from scratch + Redis
│   ├── python wsgi/           # Flask + Gunicorn WSGI app
│   ├── react/                 # React (Vite) + Nginx static serving
│   ├── asp.net-api/           # ASP.NET Core 6 Clean Architecture API
│   └── multistage-java-app/   # Java app — multistage build
│
└── docker-compose/
    ├── python-redis-mysql/    # Flask + Redis + MySQL
    ├── react-express-mongodb/ # React + Nginx + Express + MongoDB (2 networks)
    ├── asp.net-mssql/         # ASP.NET Core + SQL Server
    └── production-webapp/     # FastAPI + PostgreSQL + Redis + Nginx (3 networks)
```

---

## 🗂️ Section 1 — Dockerize Applications

Single container projects. Each project focuses on correctly writing a `Dockerfile` for a different language or framework, using **multistage builds** to produce small, production-ready images.

### Key concepts covered:
- Multistage builds to separate build-time and runtime environments
- Using virtual environments (`venv`) as portable dependency bundles (Python)
- Layer caching optimization — copying dependency files before source code
- Choosing the right base image (`alpine`, `slim`, `sdk` vs `runtime`)
- WSGI vs ASGI — Gunicorn vs Uvicorn
- Serving React as static files with Nginx

| Project | Stack | Server | Notes |
|---------|-------|--------|-------|
| `nodejs` | Node.js + Express | node | Alpine for deps → slim for runtime |
| `node-TS` | TypeScript + Node.js | node | Compile TS in build stage |
| `python wsgi` | Flask | Gunicorn | Sync WSGI — `sh` activate trick |
| `python asgi` | Custom ASGI | Uvicorn | ASGI protocol implemented from scratch |
| `react` | React (Vite) + Nginx | Nginx | `dist/` → static files, `daemon off;` |
| `asp.net-api` | ASP.NET Core 6 | Kestrel | SDK build → ASP.NET runtime, Clean Architecture |
| `multistage-java-app` | Java | JVM | Maven/Gradle build → JRE runtime |

---

## 🗂️ Section 2 — Docker Compose

Multi-container projects. Each project orchestrates multiple services with Docker Compose, focusing on **networking**, **volumes**, **environment variables**, and **service dependencies**.

### Key concepts covered:
- Docker Compose internal DNS — service names as hostnames
- Custom bridge networks for service isolation
- Named volumes for data persistence
- `expose` vs `ports` — internal vs host-accessible
- `depends_on` for startup ordering
- `env_file` for clean environment variable management
- Bind mounts for config files (Nginx)
- Nginx as a reverse proxy and load balancer

---

### 🔹 `python-redis-mysql`

**Flask + Redis + MySQL** — demonstrates how a Python app connects to two backend services over a shared network.

```
Host → python-app:9002 → redis (cache) + mysql (db)
```

- Single shared network (`app_network`)
- Redis and MySQL internal only — not exposed to host
- Named volumes for both Redis and MySQL data

---

### 🔹 `react-express-mongodb`

**React + Nginx + Express + MongoDB** — full-stack app with Nginx acting as a reverse proxy and **two isolated networks** for layered security.

```
Host → nginx:3000 → [/]     → React static files
                  → [/api/] → express:3000 → mongo:27017
```

- `react-express` network: frontend ↔ backend
- `express-mongodb` network: backend ↔ database
- Frontend cannot reach MongoDB directly
- Trivy security scanning included

---

### 🔹 `asp.net-mssql`

**ASP.NET Core 6 + SQL Server 2019** — .NET Clean Architecture API connected to Microsoft SQL Server in a container.

```
Host → api:3000 → sqlserver:1443 (internal)
```

- SQL Server requires `ACCEPT_EULA=Y` to start
- Cannot create DB/users via env vars like MySQL — uses `sa` admin user
- `ASPNETCORE_URLS` injected via Compose environment
- `TrustServerCertificate=True` required for containerized SQL Server

---

### 🔹 `production-webapp` ⭐ Final Project

**FastAPI + PostgreSQL + Redis + Nginx** — a fully async, production-ready stack with **three isolated networks**, Redis caching with invalidation, and Nginx upstream load balancing config.

```
Host → nginx:4000 → fastapi:6000 → postgres:5432
                               └─→ redis:6379
```

- Three networks: `nginx-fastapi`, `fastapi-postgress`, `fastapi-redis`
- Nginx bind-mounted config (no rebuild on change)
- Fully async FastAPI with SQLAlchemy async engine
- Redis cache with 60s TTL + cache invalidation on write
- Auto table creation on startup
- Trivy security scanning

---

## 🔒 Security Scanning

Several projects in this repo include **Trivy** image scan results. Trivy is an open-source vulnerability scanner that checks Docker images for CVEs in OS packages and language dependencies.

```bash
# Scan any image
trivy image <image-name>

# Filter by severity
trivy image --severity CRITICAL,HIGH <image-name>

# Save report
trivy image <image-name> > scan-report.txt
```

Alpine-based images (`-alpine`) are used throughout this repo to minimize the attack surface.

---

## 🧠 Core Concepts Summary

| Concept | Where Practiced |
|---------|----------------|
| Multistage builds | All dockerize-applications projects |
| Layer caching (deps first) | nodejs, asp.net-api, react |
| venv as artifact | python wsgi, python asgi, production-webapp |
| WSGI vs ASGI | python wsgi vs python asgi |
| Nginx static serving | react, react-express-mongodb |
| Nginx reverse proxy | react-express-mongodb, production-webapp |
| Docker Compose DNS | All docker-compose projects |
| Named volumes | All docker-compose projects |
| `expose` vs `ports` | react-express-mongodb, asp.net-mssql, production-webapp |
| Multiple networks | react-express-mongodb (2), production-webapp (3) |
| `env_file` | production-webapp |
| Bind mounts | production-webapp (nginx config) |
| Security scanning (Trivy) | react-express-mongodb, production-webapp |