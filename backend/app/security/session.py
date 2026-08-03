"""User session data structure for Redis storage.

Defines :class:`SessionData`, the data model representing an active user
session stored in Redis.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass
class SessionData:
    """Active user session state stored in Redis.

    Attributes:
        session_id: Unique UUID string identifying this session.
        user_id: User UUID string who owns the session.
        refresh_token_hash: SHA-256 hash of the active refresh token.
        issued_at: ISO 8601 UTC timestamp string when session was issued.
        expires_at: ISO 8601 UTC timestamp string when session expires.
        last_activity: ISO 8601 UTC timestamp string of last activity.
        user_agent: Client User-Agent header string.
        ip_address: Client IP address string.
    """

    session_id: str
    user_id: str
    refresh_token_hash: str
    issued_at: str
    expires_at: str
    last_activity: str
    user_agent: str = ""
    ip_address: str = ""

    def to_dict(self) -> dict[str, str]:
        """Convert session data to dictionary representation."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize session data to a JSON string for Redis storage."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> SessionData:
        """Construct SessionData from dictionary."""
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            refresh_token_hash=data["refresh_token_hash"],
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            last_activity=data["last_activity"],
            user_agent=data.get("user_agent", ""),
            ip_address=data.get("ip_address", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> SessionData:
        """Deserialize SessionData from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    def is_expired(self) -> bool:
        """Check if the session has passed its expiration time.

        Returns:
            True if current time exceeds expires_at, False otherwise.
        """
        try:
            exp_time = datetime.fromisoformat(self.expires_at)
            return datetime.now(UTC) >= exp_time
        except Exception:
            return True
