from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import create_db_tables
from interfaces.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_tables()
    yield


app = FastAPI(title="FoodRush User Service", lifespan=lifespan)
app.include_router(user_router, prefix="/users")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "user"}
