# 🐳 Dockerized ASP.NET Core API — Talabat

A multi-project **ASP.NET Core 6 Web API** built with **Clean Architecture**, containerized using a **multistage Docker build** to produce a lean, production-ready image.

---

## 📁 Project Structure

```
asp.net-api/
├── Talabat.Solution.sln
├── Talabat.APIs/           # Entry point — Controllers, Middleware, Program.cs
│   └── Talabat.APIs.csproj
├── Talabat.Core/           # Domain layer — Entities, Interfaces, DTOs
│   └── Talabat.Core.csproj
├── Talabat.Repository/     # Data access layer — EF Core, DbContext, Migrations
│   └── Talabat.Repository.csproj
├── Talabat.Service/        # Business logic layer — Services implementation
│   └── Talabat.Service.csproj
└── Dockerfile
```

---

## 🏛️ Architecture Overview

This project follows **Clean Architecture** (Onion Architecture) with clear separation of concerns:

| Layer | Project | Responsibility |
|-------|---------|---------------|
| API | `Talabat.APIs` | HTTP request handling, routing, middleware |
| Core | `Talabat.Core` | Domain entities, interfaces, business contracts |
| Repository | `Talabat.Repository` | EF Core DbContext, data access implementation |
| Service | `Talabat.Service` | Business logic, service implementations |

---

## 🐋 Docker Overview

This project uses a **multistage Dockerfile** to separate the build environment from the runtime environment:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `build` | `mcr.microsoft.com/dotnet/sdk:6.0` | Restore dependencies & publish the app |
| `runtime` | `mcr.microsoft.com/dotnet/aspnet:6.0` | Run the published app only |

### Why multistage?
- The **SDK image** (~700MB) contains compilers and build tools — only needed at build time.
- The **ASP.NET runtime image** (~200MB) is much smaller and contains only what's needed to run the app.
- Only the published output (`/app/publish`) is copied to the final image, keeping it clean and secure.

---

## 📄 Dockerfile Explained

```dockerfile
# Stage 1: Build & Publish
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /app

# Copy solution and all .csproj files first (layer caching optimization)
# Docker caches this layer — dotnet restore only re-runs if .csproj files change
COPY Talabat.Solution.sln .
COPY Talabat.APIs/*.csproj Talabat.APIs/
COPY Talabat.Core/*.csproj Talabat.Core/
COPY Talabat.Repository/*.csproj Talabat.Repository/
COPY Talabat.Service/*.csproj Talabat.Service/

RUN dotnet restore

# Copy everything else and publish in Release mode
COPY . .
RUN dotnet publish Talabat.APIs/Talabat.APIs.csproj \
    -c Release \
    -o /app/publish \
    --no-restore

# Stage 2: Runtime only
FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 5000

# Listen on all interfaces (0.0.0.0:5000), not just localhost
# Required for Docker networking to work correctly
ENV ASPNETCORE_URLS=http://+:5000

ENTRYPOINT ["dotnet", "Talabat.APIs.dll"]
```

---

## ⚙️ Configuration — `appsettings.json`

The app uses the following configuration sections:

| Section | Description |
|---------|-------------|
| `ConnectionStrings.DefaultConnection` | Main SQL Server database connection |
| `ConnectionStrings.IdentityConnection` | Identity/Auth SQL Server database connection |
| `JWT.Key` | Secret key used to sign JWT tokens |
| `JWT.Issure` | Token issuer (API base URL) |
| `JWT.Audience` | Token audience |
| `JWT.ExpireTimeInDays` | Token expiry duration |

> ⚠️ **Important:** The `appsettings.json` contains sensitive data (JWT secret key, DB connection strings). Never commit real credentials to source control. Use environment variables or Docker secrets in production.

### Recommended: Override config via environment variables at runtime

```bash
docker run -p 5000:5000 \
  -e ConnectionStrings__DefaultConnection="Server=your-server;..." \
  -e JWT__Key="your-secret-key" \
  talabat-api
```

---

## 🛠️ Build & Run

### 1. Build the Docker image

```bash
docker build -t talabat-api .
```

### 2. Run the container

```bash
docker run -p 5000:5000 talabat-api
```

### 3. Access the API

```bash
curl http://localhost:5000/api/WeatherForecast
```

Or open Swagger UI (if enabled in development):

```
http://localhost:5000/swagger
```

---

## 💡 Key Concepts 

- ✅ Multistage Docker builds for ASP.NET Core
- ✅ Layer caching optimization (copy `.csproj` files before source code)
- ✅ Separating SDK (build) from ASP.NET runtime (run) images
- ✅ Clean Architecture with 4 project layers
- ✅ JWT Authentication configuration
- ✅ Configuring `ASPNETCORE_URLS` for Docker networking
- ✅ Publishing in Release mode with `--no-restore` for efficiency