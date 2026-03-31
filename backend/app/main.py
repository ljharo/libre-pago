from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from alembic import command
from alembic.config import Config
from app.config import settings
from app.database import SessionLocal, engine
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware
from app.models import User
from app.routers import ads, auth, conversations, csat, import_, lifecycles, mappings, users
from app.routers.auth import get_password_hash

setup_logging()


def run_migrations():
    try:
        from sqlalchemy import inspect, text

        from app.database import engine

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "contacts" in tables:
            print("Tables already exist, skipping migrations")
            return

        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Migration error: {e}")


def create_default_admin():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == settings.admin_username).first()
        if existing_admin:
            print(f"Admin user already exists: {settings.admin_username}")
        else:
            admin = User(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: {settings.admin_username}")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    run_migrations()
    create_default_admin()

    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend API for LibrePago - Spreadsheets management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://libre-pago.poderosaccess.dpdns.org",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
