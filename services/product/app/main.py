from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import SessionLocal, create_db_tables
from infrastructure.seed_data import seed_initial_data
from interfaces.routers.product_router import router as product_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_tables()
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="FoodRush Product Service", lifespan=lifespan)
app.include_router(product_router, prefix="/products")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "product"}
