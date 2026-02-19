import os
import json
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import redis.asyncio as redis

# ==============================
# Environment Variables
# ==============================

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "mydb")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# ==============================
# Database Setup (ASYNC)
# ==============================

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

# ==============================
# FastAPI App
# ==============================

app = FastAPI()

# Redis (ASYNC)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# ==============================
# Schemas
# ==============================

class UserCreate(BaseModel):
    name: str
    email: str

# ==============================
# Dependency
# ==============================

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ==============================
# Startup Event (Create Tables)
# ==============================

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ==============================
# Routes
# ==============================

@app.post("/users")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Invalidate cache
    await redis_client.delete("users_cache")

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
    }

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    cached = await redis_client.get("users_cache")

    if cached:
        return json.loads(cached)

    result = await db.execute(text("SELECT id, name, email FROM users"))
    rows = result.fetchall()

    data = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]

    await redis_client.set("users_cache", json.dumps(data), ex=60)

    return data

@app.get("/")
async def root():
    return {"status": "🔥 Fully Async Production Ready"}

@app.get("/redis")
async def test_redis():
    try:
        await redis_client.set("fastapi_key", "Hello from Async Redis!", ex=60)
        val = await redis_client.get("fastapi_key")
        return {"redis_value": val}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/postgres")
async def test_postgres(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT version();"))
        version = result.scalar()
        return {"postgres_version": version}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ==============================
# Main
# ==============================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6000)
