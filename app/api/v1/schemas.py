"""HTTP request and response schemas."""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class SearchRequestSchema(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int | None = Field(default=None, ge=1)
    threshold: float | None = Field(default=None, ge=-1.0, le=1.0)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value


class IndexVideoRequestSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(default="", max_length=10_000)
    tags: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        return [tag.strip() for tag in values if tag.strip()]
