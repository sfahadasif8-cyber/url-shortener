from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_link():
    response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["original_url"] == "https://example.com/"
    assert len(data["short_code"]) == 6
    assert "created_at" in data


def test_redirect_records_click():
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

    stats_response = client.get(f"/links/{short_code}/stats")

    assert stats_response.status_code == 200

    stats = stats_response.json()

    assert stats["short_code"] == short_code
    assert stats["original_url"] == "https://example.com/"
    assert stats["click_count"] == 1

def test_missing_link_returns_404():
    response = client.get("/doesnotexist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short link not found"}


def test_multiple_clicks_increment_count():
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


def test_stats_missing_link_returns_404():
    response = client.get(
        "/links/doesnotexist/stats"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Short link not found"
    }
def test_invalid_url_returns_422():
    response = client.post(
        "/links",
        json={"original_url": "not-a-url"},
    )

    assert response.status_code == 422
