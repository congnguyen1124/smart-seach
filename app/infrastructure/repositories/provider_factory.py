"""Build the configured video repository adapter."""

from app.config.settings import Settings
from app.domain.ports.video_search_repository import VideoSearchRepository
from app.infrastructure.database.pgvector_video_repository import (
    PgVectorVideoRepository,
)
from app.infrastructure.repositories.in_memory_video_repository import (
    InMemoryVideoRepository,
)


def create_video_repository(settings: Settings) -> VideoSearchRepository:
    if settings.storage_backend == "postgres":
        if settings.database_url is None:
            raise ValueError("DATABASE_URL is required for PostgreSQL storage")
        return PgVectorVideoRepository(
            database_url=settings.database_url,
            embedding_dimension=settings.embedding_dimension,
            connect_timeout_seconds=settings.database_connect_timeout_seconds,
        )
    return InMemoryVideoRepository()
