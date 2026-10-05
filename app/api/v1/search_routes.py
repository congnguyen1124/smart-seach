"""Search endpoint."""

from flask import Blueprint, current_app, jsonify, request

from app.api.v1.schemas import SearchRequestSchema
from app.application.dto import SearchRequest

search_blueprint = Blueprint("search_v1", __name__)


@search_blueprint.post("/search")
def search():
    dependencies = current_app.extensions["smart_search"]
    settings = dependencies["settings"]
    payload = SearchRequestSchema.model_validate(request.get_json(silent=True) or {})

    limit = payload.limit or settings.default_search_limit
    if limit > settings.max_search_limit:
        return jsonify(
            {
                "error": "validation_error",
                "details": [
                    {
                        "loc": ["limit"],
                        "msg": f"limit must be less than or equal to {settings.max_search_limit}",
                        "type": "less_than_equal",
                    }
                ],
            }
        ), 400

    threshold = (
        payload.threshold
        if payload.threshold is not None
        else settings.default_search_threshold
    )
    result = dependencies["search_use_case"].execute(
        SearchRequest(
            query=payload.query,
            limit=limit,
            threshold=threshold,
            mode=payload.mode,
        )
    )

    return jsonify(
        {
            "query": result.query,
            "threshold": result.threshold,
            "mode": result.mode,
            "count": len(result.items),
            "items": [
                {
                    "id": str(item.video_id),
                    "title": item.title,
                    "description": item.description,
                    "tags": list(item.tags),
                    "score": round(item.score, 4),
                }
                for item in result.items
            ],
        }
    )
