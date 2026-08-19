"""Request-scoped context object.

The ``RequestContext`` carries the identifying information of a single
incoming request: the request identifier, the time the request was received,
and the correlation identifiers used to trace it across services.
"""

from datetime import datetime

from pydantic import BaseModel


class RequestContext(BaseModel):
    """Immutable identifying metadata for a single request.

    Attributes:
        request_id: Unique identifier for the request.
        timestamp: Time the request entered the application.
        correlation_id: Identifier grouping related requests.
        trace_id: Trace identifier once a tracing backend is wired in.
        user_id: Identifier of the authenticated user, when available.
        organization_id: Identifier of the authenticated organization, when
            available.
    """

    request_id: str
    timestamp: datetime
    correlation_id: str
    trace_id: str | None = None
    user_id: str | None = None
    organization_id: str | None = None
