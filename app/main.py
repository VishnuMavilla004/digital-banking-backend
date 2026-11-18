import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.exception_handlers import (
    sqlalchemy_exception_handler,
    unexpected_exception_handler,
)
from app.logging_config import configure_logging
from app.routers import accounts, auth, users

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Banking Backend",
    description="A banking backend built with Python and FastAPI",
    version="1.0.0",
)

app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(accounts.router)


@app.get("/")
def root():
    return {"message": "Digital Banking Backend is running"}


@app.get("/health/live", include_in_schema=False)
def liveness_check():
    return {"status": "alive"}


@app.get("/health/ready", include_in_schema=False)
def readiness_check(
    db: Annotated[Session, Depends(get_db)],
):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
        }

    except Exception:
        logger.exception("Readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        ) from None


@app.get("/health", tags=["Health"])
def health_check(
    db: Annotated[Session, Depends(get_db)],
):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        ) from None
