from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    original_url: HttpUrl


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

