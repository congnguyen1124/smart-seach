"""Video indexing and lookup endpoints."""

from uuid import UUID

from flask import Blueprint, current_app, jsonify, request

from app.api.v1.schemas import IndexVideoRequestSchema
from app.application.dto import IndexVideoRequest

video_blueprint = Blueprint("videos_v1", __name__)


@video_blueprint.post("/videos/index")
def index_video():
    dependencies = current_app.extensions["smart_search"]
    payload = IndexVideoRequestSchema.model_validate(request.get_json(silent=True) or {})
    result = dependencies["index_use_case"].execute(
        IndexVideoRequest(
            video_id=payload.id,
            title=payload.title,
            description=payload.description,
            tags=tuple(payload.tags),
        )
    )
    return jsonify(
        {
            "id": str(result.id),
            "title": result.title,
            "description": result.description,
            "tags": list(result.tags),
            "indexed": True,
        }
    ), 201


@video_blueprint.get("/videos/<uuid:video_id>")
def get_video(video_id: UUID):
    repository = current_app.extensions["smart_search"]["repository"]
    video = repository.get(video_id)
    if video is None:
        return jsonify({"error": "not_found", "message": "video was not found"}), 404

    return jsonify(
        {
            "id": str(video.id),
            "title": video.title,
            "description": video.description,
            "tags": list(video.tags),
        }
    )
