from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware
from app.routers import ads, conversations, csat, import_, lifecycles, mappings

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend API for LibrePago - Spreadsheets management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)

app.include_router(conversations.router)
app.include_router(lifecycles.router)
app.include_router(ads.router)
app.include_router(csat.router)
app.include_router(mappings.router)
app.include_router(import_.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.app_name}
