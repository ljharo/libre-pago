from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal, engine
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware
from app.models import User
from app.routers import ads, auth, conversations, csat, import_, lifecycles, mappings, users
from app.routers.auth import get_password_hash

setup_logging()


def create_default_admin():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not existing_admin:
            admin = User(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: {settings.admin_username}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    create_default_admin()

    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend API for LibrePago - Spreadsheets management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(lifecycles.router)
app.include_router(ads.router)
app.include_router(csat.router)
app.include_router(mappings.router)
app.include_router(import_.router)
app.include_router(users.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.app_name}
