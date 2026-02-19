# 🐳 Docker Compose — React + Express + MongoDB

A full-stack application with a **React** frontend, **Express.js** backend, and **MongoDB** database, orchestrated with Docker Compose. Nginx acts as a **reverse proxy** — serving the React app and forwarding API requests to the backend, with **two isolated networks** for security.

---

## 📁 Project Structure

```
react-express-mongodb/
├── frontend/
│   ├── src/                  # React source code
│   ├── package.json
│   ├── nginx.conf            # Nginx reverse proxy config
│   └── Dockerfile
├── backend/
│   ├── server.js             # Express entry point
│   ├── config/
│   │   └── config.json       # MongoDB connection config
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── imagealpine               # Trivy scan output — alpine-based image report
└── output.png                # Trivy scan output screenshot
```

---

## 🏗️ Architecture

```
                         ┌──────────────────────────────────────────────┐
                         │              react-express network            │
                         │                                               │
Browser ──▶ Host:3000 ──▶│  frontend (Nginx:80)                         │
                         │       │                                       │
                         │  GET /        → serves React static files    │
                         │  GET /api/*   → proxy_pass ──▶ backend:3000  │
                         │                       │                       │
                         └───────────────────────│───────────────────────┘
                                                 │
                         ┌───────────────────────│───────────────────────┐
                         │          express-mongodb network              │
                         │                       │                       │
                         │               backend (Express:3000)          │
                         │                       │                       │
                         │               mongo:27017                     │
                         │               (mongo-data volume)             │
                         └──────────────────────────────────────────────┘
```

### Two Networks — Why?
| Network | Members | Purpose |
|---------|---------|---------|
| `react-express` | frontend, backend | Frontend can reach backend via Nginx proxy |
| `express-mongodb` | backend, mongo | Backend can reach MongoDB |

The frontend **cannot directly reach MongoDB** — it has no access to the `express-mongodb` network. This mirrors real production security where the database is completely isolated from the public-facing layer.

---

## 🐋 Docker Compose Breakdown

### `frontend` (React + Nginx)
- Built from `frontend/Dockerfile`
- Exposed on host port `3000`, internal Nginx port `80`
- Serves the React static files and proxies `/api/` requests to the backend
- Depends on `backend`
- Connected to `react-express` network only

### `backend` (Express.js)
- Built from `backend/Dockerfile`
- **Not exposed to host** — only reachable inside `react-express` network
- All traffic reaches it through Nginx, not directly
- Connected to both `react-express` and `express-mongodb` networks (the bridge between frontend and DB layers)
- Depends on `mongo`

### `mongo` (MongoDB)
- Official `mongo:4.2.0` image
- **Not exposed to host** — uses `expose: 27017` (container-internal only, not host-mapped)
- Connected to `express-mongodb` network only
- Data persisted in `mongo-data` named volume

---

## 🔁 Nginx as Reverse Proxy — `nginx.conf` Explained

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html index.htm;

    # React SPA fallback — handles client-side routing
    location / {
        try_files $uri /index.html;
    }

    # Proxy API requests to the Express backend
    location /api/ {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### How traffic flows:
- `GET /` → Nginx serves `index.html` → React app loads in the browser
- `GET /some-page` → React Router handles it client-side (SPA fallback)
- `GET /api/todos` → Nginx proxies to `http://backend:3000/api/todos` → Express handles it

### Why `try_files $uri /index.html`?
React uses client-side routing. If you refresh the page on `/about`, Nginx looks for a file called `about` — it doesn't exist. Without this fallback, Nginx returns a 404. With `try_files`, it falls back to `index.html` and lets React Router handle the route.

### Why `proxy_pass http://backend:3000`?
`backend` is the Docker Compose service name — Docker's internal DNS resolves it to the backend container's IP automatically.

---

## 📄 Dockerfiles Explained

### Frontend (React + Vite → Nginx)

```dockerfile
# Stage 1: Build React app
FROM node:18-alpine AS builder
WORKDIR /app
COPY ./package*.json .
RUN npm install
COPY . .
RUN npm run build          # outputs to /app/build

# Stage 2: Serve with Nginx + custom config
FROM nginx:stable-alpine3.23-slim
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf   # override default Nginx config
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend (Express.js)

```dockerfile
# Stage 1: Install only production dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY ./package*.json .
RUN npm ci --only=production   # skips devDependencies — smaller, more secure image

# Stage 2: Run with slim image
FROM node:18-slim
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

> `npm ci --only=production` installs only production dependencies, skipping dev tools like nodemon, jest, etc. This keeps the final image smaller and more secure.

---

## 🍃 MongoDB Service Name Matters

```yaml
mongo:         # ← service name MUST be "mongo"
  image: mongo:4.2.0
```

In `config/config.json`:
```json
"MONGODB_URI": "mongodb://mongo:27017/TodoAppTest"
```

The connection string uses `mongo` as the hostname — this must match the **exact service name** in `docker-compose.yml`. Docker's DNS resolves `mongo` to the container's IP. If you rename the service, the connection string must be updated too.

---

## 🔌 `expose` vs `ports` — What's the Difference?

```yaml
mongo:
  expose:
    - 27017    # container-internal only, NOT accessible from host
```

| | `ports` | `expose` |
|--|---------|---------|
| Accessible from host | ✅ Yes | ❌ No |
| Accessible from other containers | ✅ Yes | ✅ Yes |
| Use case | Services you need to access from your machine | Internal services (DB, cache) |

MongoDB uses `expose` because only the backend needs to reach it — there's no reason to expose it to your machine in production.

---

## 💾 Volumes

| Volume | Mounted At | Purpose |
|--------|-----------|---------|
| `mongo-data` | `/data/db` | Persists MongoDB data across container restarts |

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

### Access the app

```
http://localhost:3000
```

API requests from the frontend go to `/api/*` and are proxied to Express automatically.

### Stop containers

```bash
docker-compose down
```

### Stop and remove volumes (wipes MongoDB data)

```bash
docker-compose down -v
```

---

## 🔒 Security Scanning with Trivy

All images in this project were scanned with **[Trivy](https://github.com/aquasecurity/trivy)** — an open-source vulnerability scanner for Docker images. Scan results are included in the repo for reference.

| File | Description |
|------|-------------|
| `imagealpine` | Trivy scan output for the alpine-based image (text report) |
| `output.png` | Screenshot of Trivy scan results |

### What is Trivy?
Trivy scans Docker images for:
- **OS vulnerabilities** — known CVEs in the base image packages
- **Library vulnerabilities** — vulnerable versions of npm, pip, etc. packages
- **Severity levels** — CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN

### How to scan the images yourself

#### Install Trivy
```bash
# macOS
brew install trivy

# Linux
sudo apt-get install trivy

# Or via Docker (no install needed)
docker run aquasec/trivy image <image-name>
```

#### Scan the frontend image
```bash
# Build first
docker build -t react-frontend ./frontend

# Scan
trivy image react-frontend
```

#### Scan the backend image
```bash
# Build first
docker build -t express-backend ./backend

# Scan
trivy image express-backend
```

#### Scan a pulled image (e.g. MongoDB)
```bash
trivy image mongo:4.2.0
```

#### Scan and filter by severity
```bash
# Show only CRITICAL and HIGH vulnerabilities
trivy image --severity CRITICAL,HIGH react-frontend
```

#### Save scan output to a file
```bash
trivy image react-frontend > imagealpine
```

### Why Alpine?
Alpine-based images (`node:18-alpine`, `nginx:stable-alpine`) generally have **fewer vulnerabilities** than Debian/Ubuntu-based images because they ship with a minimal set of packages. This is one of the key security benefits of using Alpine as a base image.

> 💡 **Tip:** Always scan your images before pushing to a registry or deploying to production. Consider adding Trivy to your CI/CD pipeline to catch vulnerabilities automatically.

---

## 💡 Key Concepts Practiced

- ✅ Full-stack Docker Compose orchestration (React + Express + MongoDB)
- ✅ Nginx as a reverse proxy — serving static files + proxying API requests
- ✅ React SPA fallback with `try_files $uri /index.html`
- ✅ Two isolated networks for layered security (frontend ↔ backend ↔ DB)
- ✅ `expose` vs `ports` — internal vs host-accessible ports
- ✅ Docker internal DNS — service names as hostnames
- ✅ `npm ci --only=production` for lean backend images
- ✅ Named volumes for MongoDB data persistence
- ✅ Backend not exposed to host — all traffic goes through Nginx
- ✅ Multistage builds for both frontend and backend
- ✅ Image security scanning with Trivy (CVE detection)
- ✅ Alpine-based images for reduced attack surface