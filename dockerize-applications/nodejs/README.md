# 🐳 Dockerized Node.js Express App

A simple **Express.js** application containerized using a **multistage Docker build** to keep the final image as small and production-ready as possible.

---

## 📁 Project Structure

```
nodejs/
├── server.js
├── package.json
├── package-lock.json
└── Dockerfile
```

---

## 🚀 App Overview

A minimal Express.js server that responds with a friendly message on the root route.

- **Route:** `GET /`
- **Response:** `Hello from Docker! 🐳`
- **Port:** `3000`

---

## 🐋 Docker Overview

This project uses a **multistage Dockerfile** to optimize the final image size:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `deps` | `node:18-alpine` | Install npm dependencies |
| final | `node:18-slim` | Run the app with only what's needed |

### Why multistage?
- The `alpine` image is used in the first stage just to install dependencies — it's lightweight and fast.
- The final image is based on `node:18-slim`, which is a more stable, slim Debian-based image.
- Only the `node_modules` folder is copied from the first stage, keeping build tools and unnecessary files out of the final image.

---

## 🛠️ Build & Run

### 1. Build the Docker image

```bash
docker build -t nodejs-app .
```

### 2. Run the container

```bash
docker run -p 3000:3000 nodejs-app
```

### 3. Access the app

Open your browser or use curl:

```bash
curl http://localhost:3000
# Hello from Docker! 🐳
```

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Install dependencies using Alpine (lightweight)
FROM node:18-alpine AS deps
WORKDIR /app
COPY ./package*.json .
RUN npm install

# Stage 2: Run the app using slim image (stable + small)
FROM node:18-slim
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules  # copy only deps from stage 1
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `express` | Web framework for Node.js |

---

## 💡 Key Concepts Practiced

- ✅ Multistage Docker builds
- ✅ Reducing final image size by separating build and runtime stages
- ✅ Copying only necessary artifacts between stages
- ✅ Exposing and mapping container ports