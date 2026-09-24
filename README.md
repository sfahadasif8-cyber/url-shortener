URL Shortener API

A production-oriented URL shortener API built with FastAPI, PostgreSQL, SQLAlchemy, Docker, Nginx, and GitHub Actions.

The application generates short URLs, redirects users to the original URL, records click activity, and provides basic analytics for each shortened link.

Features

1. Create shortened URLs
2. Automatic 6-character short-code generation
3. Short-code collision checking
4. HTTP 307 redirects
5. Click tracking
6. Referrer tracking
7. User-agent tracking
8. SHA-256 IP hashing for privacy-conscious analytics
9. Click statistics endpoint
10. Interactive web frontend
11. Existing-link analytics tracker
12. Automatic analytics refresh
13. Manual analytics refresh
14. Copy generated short URLs
15. PostgreSQL database
16. SQLAlchemy ORM
17. Pydantic validation
18. Automated tests with Pytest
19. Dockerized application
20. Docker Compose multi-container setup
21. Nginx reverse proxy
22. GitHub Actions CI
23. GitHub Actions Docker image publishing
24. GitHub Container Registry (GHCR)
25. PostgreSQL service in CI
26. Persistent PostgreSQL storage

Architecture

Client
  │
  ▼
Nginx
  │
  ▼
FastAPI
  │
  ├── Links
  │
  ├── Redirects
  │
  └── Analytics
       │
       ▼
   PostgreSQL

Frontend

The FastAPI application also serves an interactive browser-based frontend.

The frontend allows users to:

- Create short URLs
- Copy generated URLs
- Open generated short URLs
- View click counts
- Refresh analytics manually
- Automatically refresh analytics
- Track analytics for an existing short URL

The frontend is built with plain HTML, CSS, and JavaScript and is served directly by FastAPI.

CI/CD Pipeline

Git Push
   │
   ▼
GitHub Actions
   │
   ├── Install dependencies
   │
   ├── Start PostgreSQL
   │
   ├── Run Pytest
   │
   └── Build Docker Image
          │
          ▼
         GHCR

Tech Stack

Technology	        Purpose
Python	            Backend language
FastAPI	            REST API framework
PostgreSQL	        Relational database
SQLAlchemy	        ORM and database access
Pydantic	        Request/response validation
Pytest	            Automated testing
Docker	            Application containerization
Docker Compose	    Multi-container orchestration
Nginx	              Reverse proxy
GitHub Actions  	  Continuous integration
Git	                Version control
GitHub Container Registry    Docker image registry
HTML/CSS/JavaScript          Interactive web frontend

API Endpoints

Health Check

GET /health

Returns:

{
  "status": "ok"
}

Create Short Link

POST /links

Request:

{
  "original_url": "https://example.com"
}
Example response:

{
  "id": 1,
  "short_code": "aB12xY",
  "original_url": "https://example.com/",
  "created_at": "2026-09-23T22:51:28.946086Z"
}

Redirect

GET /{short_code}

Redirects the request to the original URL and records the click.

Link Statistics

GET /links/{short_code}/stats

Example response:

{
  "short_code": "aB12xY",
  "original_url": "https://example.com/",
  "created_at": "2026-09-23T22:51:28.946086Z",
  "click_count": 1
}

Database Model

The application uses two main tables:

Links

links
├── id
├── short_code
├── original_url
└── created_at

Clicks

clicks
├── id
├── link_id
├── clicked_at
├── referrer
├── user_agent
└── ip_hash

Each click is associated with its corresponding shortened link through a foreign key.

Running Locally

1. Clone the repository
git clone https://github.com/sfahadasif8-cyber/url-shortener.git
cd url-shortener

2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt
pip install pytest httpx

4. Start PostgreSQL
docker compose up -d db

5. Configure the database
export DATABASE_URL="postgresql+psycopg://urluser:urlpassword@localhost:5433/urlshortener"

6. Start FastAPI

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

Running with Docker Compose:

Build and start the complete stack:

docker compose up -d --build

The services are:

FastAPI  →  port 8001
PostgreSQL  →  port 5433
Nginx  →  port 8080

The application can then be accessed through Nginx:

http://127.0.0.1:8080

Check the containers:

docker compose ps

Testing

Run the test suite locally:

pytest -q

The project currently contains tests covering:

1. Health checks
2. URL creation
3. Short-code generation
4. Redirect behavior
5. Click recording
6. Multiple clicks counting
7. Statistics
8. Missing links

Continuous Integration:

GitHub Actions automatically runs the test suite whenever changes are pushed to main or a pull request targets main.

The CI environment:
1. Checks out the repository
2. Installs Python 3.14
3. Starts PostgreSQL 17
4. Installs project dependencies
5. Runs the Pytest test suite

This ensures the backend is tested automatically before changes are considered ready.

Privacy

IP addresses are not stored directly.

When a request is redirected, the client's IP address is processed using SHA-256 hashing before being stored as ip_hash.

This allows the application to associate requests with a hashed identifier without storing the raw IP address.

Project Structure

url-shortener/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── tests/
│   └── test_main.py
├── nginx/
│   └── default.conf
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md

Future Improvements

Planned improvements include:

1. Detailed analytics over time
2. Top referrers
3. Rate limiting
4. Authentication
5. User-owned links
6. Custom short codes
7. Cloud deployment
8. Automated deployment through CI/CD
9. Infrastructure as Code with Terraform
10. Production monitoring and logging

Author

Fahad Asif

Backend Developer focused on Python, FastAPI, PostgreSQL, Docker, and CI/CD.

GitHub: https://github.com/sfahadasif8-cyber