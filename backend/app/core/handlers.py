"""Global exception handlers.

Register these handlers on the FastAPI application to translate raised
exceptions into a consistent JSON error response. Python tracebacks are
never exposed to clients; unexpected failures are logged server-side with
full context.
"""

from typing import Any, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.types import ExceptionHandler

from app.core.error_codes import (
    HTTP_ERROR,
    REQUEST_VALIDATION_ERROR,
    UNHANDLED_ERROR,
)
from app.core.exceptions import TWIBException
from app.core.logging import get_logger
from app.schemas.response import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def _error_payload(
    code: str,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    """Build the consistent error response body.

    Args:
        code: Machine-readable error code.
        message: Human-readable error message.
        details: Optional structured information about the error.

    Returns:
        A dictionary matching the shared :class:`ErrorResponse` contract.
    """
    return ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details),
    ).model_dump(mode="json", exclude_none=True)


async def twib_exception_handler(request: Request, exc: TWIBException) -> JSONResponse:
    """Handle application exceptions derived from :class:`TWIBException`.

    Args:
        request: The active FastAPI request.
        exc: The raised application exception.

    Returns:
        A JSON response built from the exception attributes.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.error_code, exc.message, exc.details),
    )


async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors raised by FastAPI.

    Args:
        request: The active FastAPI request.
        exc: The validation error raised by FastAPI.

    Returns:
        A JSON response with the validation details.
    """
    errors = []
    for error in exc.errors():
        item = dict(error)
        item.pop("ctx", None)
        item.pop("url", None)
        errors.append(item)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=_error_payload(
            REQUEST_VALIDATION_ERROR,
            "Request validation failed.",
            details=errors,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions raised by FastAPI and Starlette.

    Args:
        request: The active FastAPI request.
        exc: The raised HTTP exception.

    Returns:
        A JSON response carrying the HTTP error details.
    """
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
        details = None
    else:
        message = "Request failed."
        details = detail

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(HTTP_ERROR, message, details),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any exception that no other handler covers.

    The full traceback is logged server-side and a generic response is
    returned so internal details are never exposed to the client.

    Args:
        request: The active FastAPI request.
        exc: The unexpected exception.

    Returns:
        A generic internal error response.
    """
    logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(UNHANDLED_ERROR, "An unexpected error occurred."),
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Register every global exception handler on a FastAPI application.

    Each handler is registered once; later registrations override earlier
    defaults for the same exception type without duplicating work.

    Args:
        application: The FastAPI application to configure.
    """
    application.add_exception_handler(
        TWIBException,
        cast(ExceptionHandler, twib_exception_handler),
    )
    application.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, request_validation_handler),
    )
    application.add_exception_handler(
        HTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    application.add_exception_handler(Exception, unhandled_exception_handler)
