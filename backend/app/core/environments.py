"""Application environment definitions.

The environment is selected through the ``APP_ENV`` environment variable.
"""

from enum import Enum


class Environment(str, Enum):
    """Supported application environments.

    The string value is what must be set in ``APP_ENV``.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
