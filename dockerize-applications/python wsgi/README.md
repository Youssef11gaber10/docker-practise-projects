# 🐳 Dockerized Python WSGI App — Flask + Gunicorn

A minimal **Flask** web application served with **Gunicorn**, containerized using a **multistage Docker build** with a virtual environment. This project demonstrates the WSGI stack and how it differs from ASGI.

---

## 📁 Project Structure

```
python-wsgi/
├── app.py                # Flask application
├── requirements.txt      # Python dependencies
└── Dockerfile
```

---

## 🚀 App Overview

A simple Flask app with a single route:

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/` | `Hello from Docker! 🐳` |

---

## ⚡ WSGI vs ASGI — What's the Difference?

| | WSGI | ASGI |
|--|------|------|
| **Protocol** | Synchronous | Asynchronous |
| **Framework examples** | Flask, Django | FastAPI, Starlette |
| **Server** | Gunicorn | Uvicorn |
| **Concurrency** | Multi-process / multi-thread | Async / await |
| **Streaming** | Limited | Native support |
| **WebSockets** | ❌ Not supported | ✅ Supported |

> This app uses **Gunicorn** as the process manager and WSGI server because Flask is a **synchronous** framework. Uvicorn is not used here — it's designed for ASGI apps like FastAPI.

---

## 🐋 Docker Overview

This project uses a **multistage Dockerfile** with a **Python virtual environment** to keep the final image lean:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `build` | `python:3.11` | Create venv & install dependencies |
| final | `python:3.11-slim` | Run the app with only the venv |

### Why this approach?
- A **venv** is created in the build stage and all packages (Flask + Gunicorn) are installed into it.
- Only the `/opt/venv` directory is copied to the slim final image.
- The `PATH` env variable is updated so `gunicorn` resolves from the venv binaries directly.

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Build — create venv and install dependencies
FROM python:3.11 AS build
WORKDIR /app
COPY requirements.txt .

# Create venv, activate it, and install dependencies
# Note: '.' is used instead of 'source' because Dockerfile uses 'sh' not 'bash'
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir gunicorn

# Stage 2: Slim runtime image
FROM python:3.11-slim
COPY --from=build /opt/venv /opt/venv   # copy only the venv from build stage
WORKDIR /app
COPY . .

# Add venv to PATH so gunicorn resolves correctly
ENV PATH="$PATH:/opt/venv/bin"
# Best practice: ENV PATH="/opt/venv/bin:$PATH" (venv takes priority)

EXPOSE 6000

# Run with Gunicorn — 3 workers for handling concurrent requests
# --bind 0.0.0.0:6000 is required for Gunicorn to be accessible outside the container
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:6000", "--workers", "3"]
```

### Why `--bind 0.0.0.0:6000`?
Gunicorn by default binds to `127.0.0.1` (localhost only). Inside Docker, this means the app is **not reachable** from outside the container. Setting `0.0.0.0` tells Gunicorn to listen on **all network interfaces**, making it accessible via the mapped port.

### Why 3 workers?
Gunicorn uses **multiple worker processes** to handle concurrent requests. A common rule of thumb is `(2 x CPU cores) + 1`. With 3 workers, the app can handle 3 simultaneous requests without blocking.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask==3.0.0` | Web framework (WSGI) |
| `gunicorn` | Production WSGI server & process manager |

---

## 🛠️ Build & Run

### 1. Build the Docker image

```bash
docker build -t python-wsgi-app .
```

### 2. Run the container

```bash
docker run -p 6000:6000 python-wsgi-app
```

### 3. Test the app

```bash
curl http://localhost:6000
# Hello from Docker! 🐳
```

---

## 🔍 Why Not Uvicorn Here?

You might see Gunicorn used with Uvicorn workers in ASGI projects like this:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app:app
```

That setup uses **Gunicorn as a process manager** and **Uvicorn as the async worker** — suitable for FastAPI or other ASGI frameworks. Since Flask is a **WSGI** framework, we use Gunicorn with its default sync workers and no Uvicorn is needed.

---

## 💡 Key Concepts 

- ✅ Multistage Docker builds for Python
- ✅ Virtual environment as a portable dependency bundle between stages
- ✅ Difference between WSGI (Flask/Gunicorn) and ASGI (FastAPI/Uvicorn)
- ✅ Using `sh`-compatible `. activate` instead of `source` in Dockerfiles
- ✅ Gunicorn `--bind 0.0.0.0` for Docker network accessibility
- ✅ Multi-worker Gunicorn setup for concurrency
- ✅ Running Flask in production with Gunicorn (not the Flask dev server)