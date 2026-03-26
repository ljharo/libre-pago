from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routers import ads, conversations, csat, import_, lifecycles, mappings

app = FastAPI(
    title=settings.app_name,
    description="Backend API for LibrePago - Spreadsheets management",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


app.include_router(conversations.router)
app.include_router(lifecycles.router)
app.include_router(ads.router)
app.include_router(csat.router)
app.include_router(mappings.router)
app.include_router(import_.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.app_name}
