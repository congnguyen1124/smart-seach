# Smart Video Search

Demo backend tìm kiếm video theo kiến trúc trong [architecture.md](architecture.md): Flask API, embedding, vector search, ranking, threshold filtering và Docker.

![Docker architecture](docker_architechture.png)

## Trạng thái hiện tại

Luồng API đã chạy đầy đủ nhưng **chưa kết nối SQL**, đúng với phạm vi triển khai hiện tại:

```text
HTTP API
  -> application use case
  -> embedding provider
  -> in-memory vector repository
  -> ranking
  -> threshold
  -> JSON response
```

- Dữ liệu index đang nằm trong bộ nhớ và mất khi container restart.
- `HashingEmbeddingProvider` là adapter mặc định, nhẹ và không cần tải model. Nó phù hợp để kiểm tra luồng kỹ thuật, không thay thế một model semantic đã huấn luyện.
- `SentenceTransformerEmbeddingProvider` đã được tách thành adapter tùy chọn.
- `VideoSearchRepository` là port để thay adapter in-memory bằng PostgreSQL + pgvector ở bước tiếp theo mà không đổi API/use case.

## Chạy bằng Docker

Yêu cầu Docker Engine hoặc Docker Desktop có Compose v2.

```bash
docker compose up --build -d
docker compose ps
curl http://localhost:8000/health
```

Kết quả health check:

```json
{
  "status": "ok",
  "storage": "in-memory",
  "embedding_provider": "hashing"
}
```

Dừng ứng dụng:

```bash
docker compose down
```

Có thể đổi cổng host mà không sửa Compose:

```bash
API_PORT=8080 docker compose up --build -d
```

## Thử luồng index và search

Index một video:

```bash
curl -X POST http://localhost:8000/api/v1/videos/index \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "ed41e827-bf98-4457-a083-f8ac87ebee80",
    "title": "Flutter Clean Architecture with Riverpod",
    "description": "Repository, DataSource and ViewModel architecture.",
    "tags": ["flutter", "riverpod", "architecture"]
  }'
```

Tìm kiếm:

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "flutter architecture using riverpod",
    "limit": 10,
    "threshold": 0.1
  }'
```

Đọc metadata theo ID:

```bash
curl http://localhost:8000/api/v1/videos/ed41e827-bf98-4457-a083-f8ac87ebee80
```

## Chạy test

Với Python 3.12+:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Sentence Transformers (tùy chọn)

Cài dependencies ML:

```bash
pip install -r requirements-ml.txt
```

Sau đó cấu hình, ví dụ:

```dotenv
EMBEDDING_PROVIDER=sentence_transformer
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_DIMENSION=768
```

Để build image kèm dependencies ML:

```bash
INSTALL_ML=true docker compose build
```

Model sẽ được tải ở lần khởi động đầu tiên. Cấu hình mặc định không bật chế độ này để image nhỏ và quá trình Docker smoke test có thể lặp lại nhanh.

## API

| Method | Endpoint | Mục đích |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/videos/index` | Tạo/cập nhật video và embedding |
| `GET` | `/api/v1/videos/{video_id}` | Đọc video trong runtime hiện tại |
| `POST` | `/api/v1/search` | Vector search, ranking, threshold và top K |

Các biến cấu hình được mô tả trong [.env.example](.env.example). `docker-compose.yml` đọc trực tiếp biến môi trường shell và có giá trị mặc định an toàn.

## Bước PostgreSQL + pgvector tiếp theo

Khi triển khai SQL, cần thêm một adapter `PgVectorVideoRepository` cho port hiện có, migration tạo `videos`/`video_embeddings`, HNSW index và wiring adapter theo `DATABASE_URL`. Contract API và logic ranking/threshold không cần thay đổi.
