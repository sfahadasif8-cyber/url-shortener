def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_link(client):
    response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["original_url"] == "https://example.com/"
    assert len(data["short_code"]) == 6
    assert "created_at" in data


def test_redirect_records_click(client):
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"

    stats_response = client.get(
        f"/links/{short_code}/stats"
    )

    assert stats_response.status_code == 200

    stats = stats_response.json()

    assert stats["short_code"] == short_code
    assert stats["original_url"] == "https://example.com/"
    assert stats["click_count"] == 1


def test_missing_link_returns_404(client):
    response = client.get("/doesnotexist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Short link not found"
    }


def test_multiple_clicks_increment_count(client):
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    for _ in range(3):
        response = client.get(
            f"/{short_code}",
            follow_redirects=False,
        )

        assert response.status_code == 307

    stats_response = client.get(
        f"/links/{short_code}/stats"
    )

    assert stats_response.status_code == 200
    assert stats_response.json()["click_count"] == 3


def test_stats_missing_link_returns_404(client):
    response = client.get(
        "/links/doesnotexist/stats"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Short link not found"
    }


def test_invalid_url_returns_422(client):
    response = client.post(
        "/links",
        json={"original_url": "not-a-url"},
    )

    assert response.status_code == 422

def test_redirect_records_click_metadata(client, db):
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    response = client.get(
        f"/{short_code}",
        headers={
            "Referer": "https://google.com",
            "User-Agent": "pytest-browser",
        },
        follow_redirects=False,
    )

    assert response.status_code == 307

    from sqlalchemy import select
    from app.models import Click

    click = db.scalar(
        select(Click).order_by(Click.id.desc())
    )

    assert click is not None
    assert click.referrer == "https://google.com"
    assert click.user_agent == "pytest-browser"
    assert click.ip_hash is not None
    assert len(click.ip_hash) == 64

def test_get_link_by_code_uses_redis_cache(client, db, monkeypatch):
    from app import crud
    from app import models
    from sqlalchemy import select

    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    cached_data = crud.redis_client.get(
        f"link:{short_code}"
    )

    assert cached_data is not None

    link = db.scalar(
        select(models.Link).where(
            models.Link.short_code == short_code
        )
    )

    assert link is not None

    def fail_database_lookup(*args, **kwargs):
        raise AssertionError(
            "Database lookup should not happen when Redis has the link"
        )

    monkeypatch.setattr(
        db,
        "scalar",
        fail_database_lookup,
    )

    cached_link = crud.get_link_by_code(
        db,
        short_code,
    )

    assert cached_link is not None
    assert cached_link.id == link.id
    assert cached_link.short_code == short_code
    assert cached_link.original_url == "https://example.com/"

def test_create_link_stores_matching_data_in_db_and_redis(client, db):
    from app import crud
    from app import models
    from sqlalchemy import select
    import json

    response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert response.status_code == 201

    data = response.json()
    short_code = data["short_code"]

    link = db.scalar(
        select(models.Link).where(
            models.Link.short_code == short_code
        )
    )

    assert link is not None
    assert link.original_url == "https://example.com/"

    cached_data = crud.redis_client.get(
        f"link:{short_code}"
    )

    assert cached_data is not None

    cached_link = json.loads(cached_data)

    assert cached_link["id"] == link.id
    assert cached_link["short_code"] == link.short_code
    assert cached_link["original_url"] == link.original_url
def test_create_link_with_custom_code(client):
    response = client.post(
        "/links",
        json={
            "original_url": "https://example.com",
            "custom_code": "fahadtest",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["short_code"] == "fahadtest"


def test_duplicate_custom_code_returns_409(client):
    first_response = client.post(
        "/links",
        json={
            "original_url": "https://example.com",
            "custom_code": "unique123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/links",
        json={
            "original_url": "https://google.com",
            "custom_code": "unique123",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Custom short code already exists"
    }
