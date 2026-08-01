"""Standard response envelope models.

Every API endpoint returns one of these envelopes so clients can rely on a
single consistent response structure across the whole platform. The
envelopes match the JSON contract already produced by the global exception
handlers in :mod:`app.core.handlers`.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Successful response envelope.

    Attributes:
        success: Always ``True`` for a successful response.
        data: The payload returned by the endpoint.
    """

    success: bool = True
    data: T


class ErrorDetail(BaseModel):
    """Structured description of an error.

    Attributes:
        code: Stable machine-readable error code.
        message: Human-readable description of the error.
        details: Optional structured information about the error.
    """

    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class ErrorResponse(BaseModel):
    """Error response envelope.

    Attributes:
        success: Always ``False`` for an error response.
        error: The structured error description.
    """

    success: bool = False
    error: ErrorDetail


class MessageResponse(BaseModel):
    """Response envelope carrying a message without a payload.

    Attributes:
        success: Always ``True`` for a successful response.
        message: Human-readable message.
    """

    success: bool = True
    message: str


class HealthResponse(BaseModel):
    """Health check response body.

    Attributes:
        status: Health state of the service.
        service: Public name of the service.
        version: Version of the service.
    """

    status: str
    service: str
    version: str
