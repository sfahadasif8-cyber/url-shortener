from app import crud


def test_generate_short_code():
    short_code = crud.generate_short_code()

    assert len(short_code) == 6
    assert short_code.isalnum()

def test_generate_short_codes_are_unique():
    codes = {
        crud.generate_short_code()
        for _ in range(1000)
    }

    assert len(codes) == 1000

def test_create_link(db):
    from app.schemas import LinkCreate

    link_data = LinkCreate(
        original_url="https://example.com"
    )

    link = crud.create_link(
        db,
        link_data,
    )

    assert link.id is not None
    assert link.short_code is not None
    assert len(link.short_code) == 6
    assert link.original_url == "https://example.com/"

def test_get_link_by_code_falls_back_to_database(db):
    from app.schemas import LinkCreate

    link_data = LinkCreate(
        original_url="https://example.com"
    )

    link = crud.create_link(
        db,
        link_data,
    )

    crud.redis_client.delete(
        f"link:{link.short_code}"
    )

    found_link = crud.get_link_by_code(
        db,
        link.short_code,
    )

    assert found_link is not None
    assert found_link.id == link.id
    assert found_link.short_code == link.short_code
    assert found_link.original_url == "https://example.com/"

def test_record_click(db):
    from app.schemas import LinkCreate
    from app.models import Click
    from sqlalchemy import select

    link = crud.create_link(
        db,
        LinkCreate(
            original_url="https://example.com"
        ),
    )

    click = crud.record_click(
        db,
        link,
        referrer="https://google.com",
        user_agent="pytest-browser",
        ip_hash="a" * 64,
    )

    assert click.id is not None
    assert click.link_id == link.id
    assert click.referrer == "https://google.com"
    assert click.user_agent == "pytest-browser"
    assert click.ip_hash == "a" * 64

    saved_click = db.scalar(
        select(Click).where(
            Click.id == click.id
        )
    )

    assert saved_click is not None