from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, Base
import app.models  # noqa: F401 — registers all models with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Inventory Management System API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

from fastapi.requests import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    with open("error.log", "a") as f:
        f.write(traceback.format_exc() + "\n")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


print("\n" + "="*50)
print("[CoreInventory] API Server is starting/reloading...")
print(f"[CoreInventory] ENV: {settings.APP_ENV}")
print(f"[CoreInventory] DB: {settings.DATABASE_URL[:20]}...")
print("="*50 + "\n")

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.FRONTEND_URL), "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
