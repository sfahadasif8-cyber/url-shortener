from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_code: Annotated[
        str | None,
        Field(
            min_length=3,
            max_length=10,
            pattern=r"^[A-Za-z0-9_-]+$",
        ),
    ] = None


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    short_code: str
    original_url: str
    created_at: datetime


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    click_count: int