from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import create_db_tables
from interfaces.routers.chat_router import router as chat_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_tables()
    yield


app = FastAPI(title="FoodRush Chat Service", lifespan=lifespan)
app.include_router(chat_router, prefix="/chat")

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "chat"}
