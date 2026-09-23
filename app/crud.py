import secrets
import string

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.schemas import LinkCreate


def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def create_link(db: Session, link_data: LinkCreate) -> models.Link:
    while True:
        short_code = generate_short_code()

        existing_link = db.scalar(
            select(models.Link).where(models.Link.short_code == short_code)
        )

        if existing_link is None:
            break

    link = models.Link(
        short_code=short_code,
        original_url=str(link_data.original_url),
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


def get_link_by_code(db: Session, short_code: str) -> models.Link | None:
    return db.scalar(
        select(models.Link).where(models.Link.short_code == short_code)
    )
def record_click(
    db: Session,
    link: models.Link,
    referrer: str | None = None,
    user_agent: str | None = None,
    ip_hash: str | None = None,
) -> models.Click:
    click = models.Click(
        link_id=link.id,
        referrer=referrer,
        user_agent=user_agent,
        ip_hash=ip_hash,
    )

    db.add(click)
    db.commit()
    db.refresh(click)

    return click
def get_link_stats(db: Session, short_code: str):
    link = get_link_by_code(db, short_code)

    if link is None:
        return None

    click_count = len(link.clicks)

    return link, click_count
