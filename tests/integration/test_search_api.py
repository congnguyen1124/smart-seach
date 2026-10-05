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


def test_keyword_search_scores_and_filters_at_40_percent(client):
    videos = [
        (
            "11111111-1111-4111-8111-111111111111",
            "PostgreSQL pgvector Semantic Search with Docker",
        ),
        (
            "22222222-2222-4222-8222-222222222222",
            "PostgreSQL pgvector Search Optimization",
        ),
        (
            "33333333-3333-4333-8333-333333333333",
            "Semantic Search Fundamentals",
        ),
        (
            "44444444-4444-4444-8444-444444444444",
            "Docker Fundamentals",
        ),
    ]
    for video_id, title in videos:
        response = client.post(
            "/api/v1/videos/index",
            json={"id": video_id, "title": title},
        )
        assert response.status_code == 201

    response = client.post(
        "/api/v1/search",
        json={
            "query": "postgresql pgvector semantic search docker",
            "mode": "keyword",
            "threshold": 0.4,
            "limit": 10,
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "keyword"
    assert payload["count"] == 3
    assert [item["score"] for item in payload["items"]] == [1.0, 0.6, 0.4]
