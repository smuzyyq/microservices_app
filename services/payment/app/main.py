from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import create_db_tables
from interfaces.routers.payment_router import router as payment_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_tables()
    yield


app = FastAPI(title="FoodRush Payment Service", lifespan=lifespan)
app.include_router(payment_router, prefix="/payments")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "payment"}
