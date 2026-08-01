"""Reusable pagination schemas.

These models describe the shape of paginated list responses. They contain
no pagination logic; the actual page calculation belongs to repositories
and services in later phases. The models are generic so they can wrap any
item type.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata describing a single page of results.

    Attributes:
        page: One-based index of the current page.
        page_size: Number of items requested per page.
        total_items: Total number of items across all pages.
        total_pages: Total number of pages available.
        has_previous: Whether a previous page exists.
        has_next: Whether a next page exists.
    """

    page: int = Field(ge=1, description="One-based index of the current page.")
    page_size: int = Field(ge=1, description="Number of items per page.")
    total_items: int = Field(ge=0, description="Total number of items across all pages.")
    total_pages: int = Field(ge=0, description="Total number of pages available.")
    has_previous: bool = Field(description="Whether a previous page exists.")
    has_next: bool = Field(description="Whether a next page exists.")


class PaginatedResponse(BaseModel, Generic[T]):
    """Response envelope for a single page of results.

    Attributes:
        success: Always ``True`` for a successful response.
        data: The items on the current page.
        pagination: Metadata describing the current page.
    """

    success: bool = True
    data: list[T]
    pagination: PaginationMeta
