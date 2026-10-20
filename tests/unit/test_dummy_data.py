import json
from pathlib import Path
from uuid import UUID


def test_dummy_data_is_large_diverse_and_image_ready():
    source = Path(__file__).parents[2] / "data" / "dummy_videos.json"
    records = json.loads(source.read_text(encoding="utf-8"))

    assert len(records) >= 100
    assert len({record["id"] for record in records}) == len(records)
    assert len({record["title"] for record in records}) == len(records)
    assert len({tag for record in records for tag in record["tags"]}) >= 75

    for record in records:
        UUID(record["id"])
        assert record["title"].strip()
        assert record["description"].strip()
        assert record["tags"]
        assert record["thumbnail_url"].startswith("https://images.unsplash.com/")
