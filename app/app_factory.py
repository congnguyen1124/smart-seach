"""Flask application factory and dependency wiring."""

from __future__ import annotations

from flask import Flask, jsonify
from pydantic import ValidationError

from app.api.v1.search_routes import search_blueprint
from app.api.v1.video_routes import video_blueprint
from app.application.index_video import IndexVideoUseCase
from app.application.search_videos import SearchVideosUseCase
from app.config.settings import Settings
from app.domain.ports.embedding_provider import EmbeddingProvider
from app.domain.ports.video_search_repository import VideoSearchRepository
from app.domain.services.ranking_service import RankingService
from app.domain.services.threshold_policy import ThresholdPolicy
from app.infrastructure.embedding.provider_factory import create_embedding_provider
from app.infrastructure.repositories.provider_factory import (
    create_video_repository,
)


def create_app(
    settings: Settings | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    repository: VideoSearchRepository | None = None,
) -> Flask:
    """Create the HTTP application and inject its concrete adapters."""

    resolved_settings = settings or Settings.from_env()
    resolved_embedding_provider = embedding_provider or create_embedding_provider(
        resolved_settings
    )
    resolved_repository = repository or create_video_repository(resolved_settings)

    search_use_case = SearchVideosUseCase(
        embedding_provider=resolved_embedding_provider,
        repository=resolved_repository,
        ranking_service=RankingService(),
        threshold_policy=ThresholdPolicy(),
        candidate_multiplier=resolved_settings.search_candidate_multiplier,
    )
    index_use_case = IndexVideoUseCase(
        embedding_provider=resolved_embedding_provider,
        repository=resolved_repository,
        model_name=resolved_settings.embedding_model,
    )

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.extensions["smart_search"] = {
        "settings": resolved_settings,
        "search_use_case": search_use_case,
        "index_use_case": index_use_case,
        "repository": resolved_repository,
    }

    app.register_blueprint(search_blueprint, url_prefix="/api/v1")
    app.register_blueprint(video_blueprint, url_prefix="/api/v1")

    @app.get("/health")
    def health() -> tuple[dict[str, str | int], int]:
        try:
            resolved_repository.health_check()
        except Exception:
            return {
                "status": "unhealthy",
                "storage": resolved_repository.backend_name,
                "embedding_provider": resolved_settings.embedding_provider,
                "embedding_dimension": resolved_settings.embedding_dimension,
            }, 503
        return {
            "status": "ok",
            "storage": resolved_repository.backend_name,
            "embedding_provider": resolved_settings.embedding_provider,
            "embedding_dimension": resolved_settings.embedding_dimension,
        }, 200

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return jsonify(
            {
                "error": "validation_error",
                "details": error.errors(include_context=False),
            }
        ), 400

    return app
