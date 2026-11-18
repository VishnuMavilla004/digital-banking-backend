import logging

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

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

# Register centralized exception handlers.
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

app.add_exception_handler(Exception, unexpected_exception_handler)


# Register API routers.
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(accounts.router)


@app.get("/")
def root():
    return {"message": "Digital Banking Backend is running"}


logger.info("Digital Banking Backend application initialized")
