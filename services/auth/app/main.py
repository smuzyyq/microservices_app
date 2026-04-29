from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import SessionLocal, create_db_tables
from infrastructure.seed_data import seed_demo_users
from interfaces.routers.auth_router import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_tables()
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()
    yield


app = FastAPI(title="FoodRush Auth Service", lifespan=lifespan)
app.include_router(auth_router, prefix="/auth")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "auth"}
