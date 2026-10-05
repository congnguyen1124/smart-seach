"""Search videos use case."""

from app.application.dto import SearchRequest, SearchResponse
from app.domain.entities.search_result import SearchResult
from app.domain.ports.embedding_provider import EmbeddingProvider
from app.domain.ports.video_search_repository import VideoSearchRepository
from app.domain.services.ranking_service import RankingService
from app.domain.services.threshold_policy import ThresholdPolicy

MINIMUM_KEYWORD_SCORE = 0.4


class SearchVideosUseCase:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        repository: VideoSearchRepository,
        ranking_service: RankingService,
        threshold_policy: ThresholdPolicy,
        candidate_multiplier: int,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._repository = repository
        self._ranking_service = ranking_service
        self._threshold_policy = threshold_policy
        self._candidate_multiplier = candidate_multiplier

    def execute(self, request: SearchRequest) -> SearchResponse:
        candidate_limit = max(request.limit * self._candidate_multiplier, 50)
        if request.mode == "keyword":
            candidates = self._repository.keyword_search(
                request.query, candidate_limit
            )
        else:
            query_vector = self._embedding_provider.embed_query(request.query)
            candidates = self._repository.semantic_search(
                query_vector, candidate_limit
            )
        ranked = self._ranking_service.rank(candidates)
        effective_threshold = (
            max(request.threshold, MINIMUM_KEYWORD_SCORE)
            if request.mode == "keyword"
            else request.threshold
        )
        filtered = self._threshold_policy.apply(ranked, effective_threshold)
        items = tuple(
            SearchResult(
                video_id=item.video_id,
                title=item.title,
                description=item.description,
                tags=item.tags,
                score=item.score,
            )
            for item in filtered[: request.limit]
        )
        return SearchResponse(
            query=request.query,
            threshold=effective_threshold,
            mode=request.mode,
            items=items,
        )
