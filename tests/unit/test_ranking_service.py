from uuid import UUID

from app.domain.entities.search_result import SearchCandidate
from app.domain.services.ranking_service import RankingService


def candidate(identifier: int, score: float) -> SearchCandidate:
    return SearchCandidate(
        video_id=UUID(int=identifier),
        title=str(identifier),
        description="",
        tags=(),
        score=score,
    )


def test_results_are_sorted_by_descending_score():
    ranked = RankingService().rank([candidate(1, 0.2), candidate(2, 0.9)])
    assert [item.score for item in ranked] == [0.9, 0.2]


def test_equal_scores_have_stable_id_order():
    ranked = RankingService().rank([candidate(2, 0.5), candidate(1, 0.5)])
    assert [item.video_id for item in ranked] == [UUID(int=1), UUID(int=2)]
