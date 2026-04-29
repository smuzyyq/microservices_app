import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import create_db_tables, get_db_connection_state, test_database_connection
from interfaces.routers.order_router import router as order_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("foodrush.order")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        create_db_tables()
        if not get_db_connection_state():
            logger.error("Order service started in degraded mode because the database is disconnected.")
    except Exception as exc:
        logger.exception("Unexpected startup error in order service: %s", exc)
    yield


app = FastAPI(title="FoodRush Order Service", lifespan=lifespan)
app.include_router(order_router, prefix="/orders")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    connected = test_database_connection()
    if connected:
        return {"status": "ok", "service": "order", "db": "connected"}
    return {"status": "degraded", "service": "order", "db": "disconnected"}
