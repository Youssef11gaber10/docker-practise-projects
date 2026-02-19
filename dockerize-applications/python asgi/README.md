# 🐳 Dockerized Python ASGI App

A **custom ASGI application** built from scratch without any web framework, containerized using a **multistage Docker build** with a virtual environment to keep the final image as small as possible.

> This project is based on the [ASGI spec](https://github.com/django/asgiref/blob/master/specs/asgi.rst) and implements the protocol manually to understand how ASGI works under the hood.

---

## 📁 Project Structure

```
python-asgi/
├── app/
│   ├── __init__.py
│   ├── redis.py          # Redis client setup
│   ├── urls.py           # URL routing
│   └── views.py          # Request handlers
├── load_testing/
│   └── load_testing.py   # Locust load testing scripts
├── asgi_app.py           # Core ASGI application class
├── main.py               # Request dispatcher / entry point
├── request.py            # HTTP request processor & Request model
├── response.py           # HTTP response model
├── requirements.txt
└── Dockerfile
```

---

## 🚀 App Overview

A minimal ASGI app that interacts with **Redis** via two endpoints:

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/get` | `key` | Fetch the value of a key from Redis |
| GET | `/set` | `key`, `value` | Set a key-value pair in Redis |

> ⚠️ **Note:** This app requires a **Redis instance** running and accessible. By default it connects to Redis on localhost at the default port `6379`.

---

## 🏗️ How ASGI Works Here

The `ASGIApplication` class implements the ASGI interface manually:

```
Request comes in
      ↓
get_request_body()    → reads body chunks from the ASGI receive channel
      ↓
HttpProcessor         → parses scope + body into a Request object
      ↓
main(request)         → routes to the correct view/handler
      ↓
start_response()      → sends HTTP status & headers via the ASGI send channel
      ↓
send_body()           → sends the response body (supports str & async generators)
```

The app supports **streaming responses** via async generators, which is one of the key advantages of ASGI over WSGI.

---

## 🐋 Docker Overview

This project uses a **multistage Dockerfile** with a **Python virtual environment** to isolate and transfer dependencies cleanly:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `build` | `python:3.10` | Create venv & install dependencies |
| final | `python:3.10-slim` | Run the app with only the venv |

### Why this approach?
- A **venv** (`/opt/venv`) is created in the build stage to collect all installed packages in one directory.
- Only that venv folder is copied to the slim final image — no pip, no build tools, no cache.
- The `PATH` env variable is updated to point to the venv's binaries so `uvicorn` can be called directly.

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Install dependencies into a virtual environment
FROM python:3.10 AS build
WORKDIR /app
COPY requirements.txt .

# Create venv and install deps inside it — all packages land in /opt/venv
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Slim runtime image
FROM python:3.10-slim
COPY --from=build /opt/venv /opt/venv   # copy only the venv from build stage
WORKDIR /app
COPY . .

# Add venv binaries to PATH so uvicorn/python commands resolve correctly
ENV PATH="$PATH:/opt/venv/bin"
# Best practice: ENV PATH="/opt/venv/bin:$PATH" (venv takes priority)

EXPOSE 6000
CMD ["uvicorn", "asgi_app:ASGIApplication", "--host", "0.0.0.0", "--port", "6000", "--loop", "asyncio"]
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `uvicorn` | 0.3.5 | ASGI server to serve the app |
| `aioredis` | 1.1.0 | Async Redis client |
| `locustio` | 0.9.0 | Load testing tool |

---

## 🛠️ Build & Run

### Prerequisites
Make sure Redis is running locally or accessible:
```bash
docker run -d -p 6379:6379 redis
```

### 1. Build the Docker image

```bash
docker build -t python-asgi-app .
```

### 2. Run the container

```bash
docker run -p 6000:6000 python-asgi-app
```

### 3. Test the endpoints

```bash
# Set a key
curl "http://localhost:6000/set?key=name&value=docker"

# Get a key
curl "http://localhost:6000/get?key=name"
```

---

## 🔬 Load Testing

The project includes a **Locust** load testing script under `load_testing/`:

```bash
locust -f load_testing/load_testing.py --host=http://localhost:6000
```

Then open `http://localhost:8089` to run the load test from the Locust UI.

---

## 💡 Key Concepts 

- ✅ Multistage Docker builds for Python
- ✅ Using a virtual environment (`venv`) as a portable dependency bundle
- ✅ Copying only the venv to the slim image (clean & minimal final image)
- ✅ Implementing the ASGI protocol from scratch (no Django, no FastAPI)
- ✅ Async request/response cycle with `send` and `receive` channels
- ✅ Streaming responses via async generators
- ✅ Async Redis integration with `aioredis`
- ✅ Running ASGI apps with `uvicorn`