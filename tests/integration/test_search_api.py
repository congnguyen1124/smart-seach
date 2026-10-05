from uuid import uuid4


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_index_then_search_video(client):
    video_id = str(uuid4())
    index_response = client.post(
        "/api/v1/videos/index",
        json={
            "id": video_id,
            "title": "Flutter Clean Architecture with Riverpod",
            "description": "Repositories, data sources and view models.",
            "tags": ["flutter", "riverpod", "architecture"],
        },
    )
    assert index_response.status_code == 201

    search_response = client.post(
        "/api/v1/search",
        json={"query": "flutter riverpod architecture", "threshold": 0.0},
    )
    assert search_response.status_code == 200
    payload = search_response.get_json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == video_id
    assert payload["items"][0]["score"] > 0


def test_invalid_blank_query_returns_400(client):
    response = client.post("/api/v1/search", json={"query": "  "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_error"


def test_search_without_matches_returns_empty_items(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "anything", "threshold": 0.9},
    )
    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_limit_above_configured_max_returns_400(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "anything", "limit": 51},
    )
    assert response.status_code == 400
