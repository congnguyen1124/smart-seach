"""Index a video's searchable content."""

from app.application.dto import IndexVideoRequest
from app.domain.entities.video import Video
from app.domain.ports.embedding_provider import EmbeddingProvider
from app.domain.ports.video_search_repository import VideoSearchRepository


class IndexVideoUseCase:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        repository: VideoSearchRepository,
        model_name: str,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._repository = repository
        self._model_name = model_name

    def execute(self, request: IndexVideoRequest) -> Video:
        video = Video(
            id=request.video_id,
            title=request.title,
            description=request.description,
            tags=request.tags,
        )
        searchable_document = self._build_searchable_document(video)
        embedding = self._embedding_provider.embed_document(searchable_document)
        self._repository.upsert(video, embedding, self._model_name)
        return video

    @staticmethod
    def _build_searchable_document(video: Video) -> str:
        return (
            f"title: {video.title}\n"
            f"description: {video.description}\n"
            f"tags: {', '.join(video.tags)}"
        )
