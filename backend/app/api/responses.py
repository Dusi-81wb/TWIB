"""Centralized helpers that build consistent API responses.

Every helper returns a :class:`starlette.responses.Response` (or
:class:`fastapi.responses.JSONResponse`) built from the shared response
schemas in :mod:`app.schemas.response`, so all endpoints return the same
envelope without re-deriving the structure in each router.
"""

from typing import Any

from fastapi import Response, status
from fastapi.responses import JSONResponse

from app.schemas.response import ErrorDetail, ErrorResponse, SuccessResponse


def success(
    data: Any,
    *,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Return a success envelope wrapping the given payload.

    Args:
        data: Payload to place inside the ``data`` field.
        status_code: HTTP status code for the response.

    Returns:
        A JSON response with the ``{"success": true, "data": ...}`` envelope.
    """
    return JSONResponse(
        status_code=status_code,
        content=SuccessResponse(data=data).model_dump(mode="json"),
    )


def created(data: Any) -> JSONResponse:
    """Return a ``201 Created`` success response.

    Args:
        data: Payload describing the created resource.

    Returns:
        A JSON response with status ``201`` and a success envelope.
    """
    return success(data, status_code=status.HTTP_201_CREATED)


def accepted(data: Any = None) -> JSONResponse:
    """Return a ``202 Accepted`` success response.

    Args:
        data: Optional payload describing the accepted operation.

    Returns:
        A JSON response with status ``202`` and a success envelope.
    """
    return success(data, status_code=status.HTTP_202_ACCEPTED)


def no_content() -> Response:
    """Return a ``204 No Content`` response with an empty body.

    Returns:
        An empty response with status ``204``.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def error(
    error_code: str,
    message: str,
    *,
    details: dict[str, Any] | list[Any] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """Return an error envelope with the shared error contract.

    Args:
        error_code: Stable machine-readable error code.
        message: Human-readable description of the error.
        details: Optional structured information about the error.
        status_code: HTTP status code for the error response.

    Returns:
        A JSON response with the ``{"success": false, "error": ...}`` envelope.
    """
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=ErrorDetail(code=error_code, message=message, details=details),
        ).model_dump(mode="json", exclude_none=True),
    )
