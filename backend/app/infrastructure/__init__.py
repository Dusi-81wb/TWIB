"""Infrastructure layer for the TWIB backend.

This package contains every external dependency adapter: the database
connection layer, ORM models, repositories, cache, vector database, and
other third-party integrations. Infrastructure code is the only layer that
may depend on a framework or external service; it implements the contracts
defined by the domain and application layers.

The current contents:

- :mod:`app.infrastructure.database`: PostgreSQL async engine, sessions, and base.
- :mod:`app.infrastructure.database.models`: SQLAlchemy 2.0 ORM persistence models.
- :mod:`app.infrastructure.repositories`: Concrete repositories and Unit of Work.
- :mod:`app.infrastructure.cache`: Redis client wrapper and connection pooling.
- :mod:`app.infrastructure.vector`: Qdrant vector store client and collection helpers.
"""

__all__: list[str] = []
