"""Video search repository port."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.search_result import SearchCandidate
from app.domain.entities.video import Video


class VideoSearchRepository(Protocol):
    def upsert(
        self, video: Video, embedding: list[float], model_name: str
    ) -> None: ...

    def get(self, video_id: UUID) -> Video | None: ...

    def semantic_search(
        self, query_vector: list[float], candidate_limit: int
    ) -> list[SearchCandidate]: ...
