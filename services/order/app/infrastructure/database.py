import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("foodrush.order.database")

engine = create_engine(settings.order_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()
db_connected = False


def test_database_connection() -> bool:
    global db_connected

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_connected = True
        logger.info("✅ Order DB connected successfully")
    except Exception as exc:
        db_connected = False
        logger.exception("❌ FATAL: Cannot connect to Order DB: %s", exc)
        logger.error("❌ DATABASE_URL: %s", settings.order_database_url)
    return db_connected


def create_db_tables() -> None:
    import infrastructure.models  # noqa: F401

    if not test_database_connection():
        logger.error("Skipping order table creation because DB connection is unavailable.")
        return

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Order DB tables ensured successfully.")
    except Exception as exc:
        logger.exception("Failed to create order DB tables: %s", exc)


def get_db_connection_state() -> bool:
    return db_connected


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
