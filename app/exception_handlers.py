import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.exception(
        "Database error | exception_type=%s | method=%s | path=%s",
        type(exc).__name__,
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unexpected application error | exception_type=%s | method=%s | path=%s",
        type(exc).__name__,
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
