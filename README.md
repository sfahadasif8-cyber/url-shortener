# URL Shortener

A production-oriented URL shortener built with FastAPI, PostgreSQL, Redis, SQLAlchemy, Docker, Nginx, GitHub Actions, and Render.

The application creates short URLs, supports custom short codes, redirects users to original URLs, records click analytics, applies Redis-backed rate limiting, and exposes statistics for each shortened link.

## Live Deployment

Production API:
https://url-shortener-ewec.onrender.com

API Documentation:
https://url-shortener-ewec.onrender.com/docs

Health check:

GET /health

Response:

{
  "status": "ok"
}

---

## Features

- Automatic 6-character short-code generation
- Custom short codes
- Short-code collision detection
- URL validation with Pydantic
- HTTP 307 redirects
- Click tracking
- Referrer tracking
- User-agent tracking
- SHA-256 IP hashing for privacy-conscious analytics
- Click statistics
- Redis URL caching
- Redis-backed rate limiting
- PostgreSQL persistence
- SQLAlchemy ORM
- Alembic database migrations
- Interactive browser frontend
- Dockerized application
- Docker Compose multi-container environment
- Nginx reverse proxy
- Automated Pytest test suite
- GitHub Actions continuous integration
- Automatic production deployment through Render

---

## Architecture

                         ┌─────────────────────┐
                         │       Client        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Nginx        │
                         │   Reverse Proxy    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       API           │
                         └──────┬───────┬──────┘
                                │       │
                    ┌───────────┘       └───────────┐
                    ▼                               ▼
             ┌──────────────┐                ┌──────────────┐
             │  PostgreSQL  │                │    Redis     │
             │              │                │              │
             │ Links        │                │ URL cache    │
             │ Clicks       │                │ Rate limits  │
             └──────────────┘                └──────────────┘

Production deployment:

Internet
   │
   ▼
Cloudflare
   │
   ▼
Render
   │
   ▼
FastAPI
   ├── Neon PostgreSQL
   └── Upstash Redis

---

## API Endpoints

### Health Check

GET /health

Response:

{
  "status": "ok"
}

### Create Short Link

POST /links

Request:

{
  "original_url": "https://example.com"
}

Example response:

{
  "id": 46,
  "short_code": "0M5ZS7",
  "original_url": "https://example.com/",
  "created_at": "2026-10-05T15:04:42.480288Z"
}

### Create Custom Short Code

Request:

{
  "original_url": "https://example.com",
  "custom_code": "fahad26"
}

Custom codes are validated and checked for collisions before creation.

### Redirect

GET /{short_code}

The endpoint records the click and returns an HTTP 307 redirect to the original URL.

### Link Statistics

GET /links/{short_code}/stats

Example:

{
  "short_code": "0M5ZS7",
  "original_url": "https://example.com/",
  "created_at": "2026-10-05T15:04:42.480288Z",
  "click_count": 1
}

---

## Rate Limiting

Link creation is protected using Redis-backed rate limiting.

Current policy:

10 link creation requests
per IP
per 60-second window

Requests exceeding the limit receive:

429 Too Many Requests

When deployed behind a proxy, the application uses the X-Forwarded-For header to identify the originating client IP.

---

## Caching

Redis is used as a cache for shortened URLs.

Redirect flow:

Request
   │
   ▼
Redis lookup
   │
   ├── Cache hit ──────► Redirect
   │
   └── Cache miss
          │
          ▼
      PostgreSQL
          │
          ▼
      Store in Redis
          │
          ▼
       Redirect

This avoids a PostgreSQL lookup for frequently accessed short URLs.

---

## Analytics

Each redirect records:

- Link ID
- Timestamp
- Referrer
- User-Agent
- SHA-256 hash of the client IP

Raw IP addresses are not stored.

Statistics use a database-side COUNT(*) query rather than loading every click record into application memory.

---

## Performance Testing

The application was load-tested locally using hey with:

1000 requests
50 concurrent clients

### Redirect Performance

Before optimization:

Throughput:       ~281 req/s
Average latency:  ~171 ms
P50 latency:      ~158 ms
P95 latency:      ~283 ms
P99 latency:      ~367 ms

After optimization:

Throughput:       ~473 req/s
Average latency:  ~100 ms
P50 latency:      ~98 ms
P95 latency:      ~156 ms
P99 latency:      ~242 ms

### Improvement

Throughput:       +68%
Average latency:  -42%
P50 latency:      -38%
P95 latency:      -45%

---

## Bottleneck Investigation

The statistics endpoint initially calculated click counts using:

len(link.clicks)

This caused SQLAlchemy to load all click records into application memory before counting them.

The implementation was changed to perform the aggregation directly in PostgreSQL:

select(func.count()).select_from(models.Click).where(
    models.Click.link_id == link.id
)

### Statistics Performance

Before:

Throughput:       ~45.6 req/s
Average latency:  ~1.04 s
P50 latency:      ~1.05 s
P95 latency:      ~1.51 s
P99 latency:      ~2.14 s

After:

Throughput:       ~639 req/s
Average latency:  ~76 ms
P50 latency:      ~74 ms
P95 latency:      ~112 ms
P99 latency:      ~157 ms

Result:

~14× higher throughput
~93% lower average latency
~93% lower P50 latency
~93% lower P99 latency

This optimization reduced unnecessary application-side data loading and allowed PostgreSQL to perform the aggregation directly.

---

## Concurrency Optimization

The API was initially running with a single Uvicorn worker.

The production container was changed to run two workers:

uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2

This increased redirect throughput from approximately:

281 req/s → 473 req/s

while significantly reducing request latency under concurrent load.

---

## Database

The application uses PostgreSQL with SQLAlchemy.

### Tables

links
├── id
├── short_code
├── original_url
└── created_at

clicks
├── id
├── link_id
├── clicked_at
├── referrer
├── user_agent
└── ip_hash

Each click is associated with its corresponding shortened link through a foreign key.

Database schema changes are managed with Alembic.

---

## Testing

The project currently has:

17 tests
17 passed

Run locally:

pytest -q

The test suite covers:

- Health checks
- URL creation
- URL validation
- Short-code generation
- Custom short codes
- Duplicate custom codes
- Redirect behavior
- Click recording
- Multiple clicks
- Statistics
- Missing links
- Rate limiting

GitHub Actions automatically runs the test suite on pushes to main and pull requests targeting main.

Current CI status:

17 passed

---

## Running Locally

### Requirements

- Python 3.14+
- Docker
- Docker Compose
- Git

### Clone

git clone https://github.com/sfahadasif8-cyber/url-shortener.git
cd url-shortener

### Python Environment

python -m venv .venv
source .venv/bin/activate

### Install Dependencies

pip install -r requirements.txt
pip install pytest httpx

### Run the Full Docker Environment

docker compose up -d --build

The local services are:

FastAPI      → 8000
PostgreSQL   → 5433
Redis        → 6379
Nginx        → 8080

The application can be accessed through:

http://127.0.0.1:8080

API documentation:

http://127.0.0.1:8080/docs

Check containers:

docker compose ps

Run tests:

pytest -q

---

## CI/CD

GitHub Actions provides automated continuous integration.

The CI pipeline:

Git Push / Pull Request
          │
          ▼
    GitHub Actions
          │
          ├── Checkout repository
          │
          ├── Setup Python 3.14
          │
          ├── Start PostgreSQL 17
          │
          ├── Start Redis 7
          │
          ├── Install dependencies
          │
          └── Run Pytest

Production deployment is handled automatically through Render after changes are pushed to main.

---

## Project Structure

url-shortener/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── redis_client.py
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
│
├── tests/
│   └── test_main.py
│
├── alembic/
│   └── versions/
│
├── nginx/
│   └── default.conf
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── entrypoint.sh
├── alembic.ini
├── requirements.txt
├── pytest.ini
└── README.md

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | REST API framework |
| PostgreSQL | Persistent relational database |
| Neon | Production PostgreSQL |
| SQLAlchemy | ORM and database access |
| Alembic | Database migrations |
| Redis | Caching and rate limiting |
| Upstash | Production Redis |
| Pydantic | Request/response validation |
| Pytest | Automated testing |
| Docker | Containerization |
| Docker Compose | Local multi-container environment |
| Nginx | Reverse proxy |
| GitHub Actions | Continuous integration |
| Render | Production deployment |
| HTML/CSS/JavaScript | Browser frontend |
| Git/GitHub | Version control |

---

## Future Improvements

Possible future extensions:

- Authentication and user accounts
- User-owned links
- Expiration dates
- Password-protected links
- Advanced analytics dashboards
- Time-series click analytics
- Top referrers
- Geographic analytics
- Structured application logging
- Production monitoring and alerting
- Terraform infrastructure
- Kubernetes deployment

---

## Author

Fahad Asif

Backend/DevOps-focused developer working with Python, FastAPI, PostgreSQL, Docker, Redis, CI/CD, and cloud infrastructure.

GitHub:

https://github.com/sfahadasif8-cyber