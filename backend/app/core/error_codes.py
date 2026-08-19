"""Central registry of machine-readable error codes.

Every error code is a stable string shared by the exception hierarchy in
:mod:`app.core.exceptions` and the global handlers in
:mod:`app.core.handlers`. The code is returned to clients inside the
``error.code`` field of the response body.
"""

VALIDATION_ERROR = "VALIDATION_ERROR"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
CONFLICT = "CONFLICT"
SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
REQUEST_VALIDATION_ERROR = "REQUEST_VALIDATION_ERROR"
HTTP_ERROR = "HTTP_ERROR"
UNHANDLED_ERROR = "UNHANDLED_ERROR"
RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
