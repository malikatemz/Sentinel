from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class EndpointCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] = "GET"
    interval_seconds: Literal[30, 60, 300, 600, 1800, 3600] = 60
    expected_status: int = Field(default=200, ge=100, le=599)


class EndpointUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    url: HttpUrl | None = None
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] | None = None
    interval_seconds: Literal[30, 60, 300, 600, 1800, 3600] | None = None
    expected_status: int | None = Field(default=None, ge=100, le=599)
    is_active: bool | None = None


class EndpointResponse(BaseModel):
    id: UUID
    name: str
    url: str
    method: str
    interval_seconds: int
    expected_status: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Computed fields added by the router
    last_check_at: datetime | None = None
    last_status: int | None = None
    is_up: bool | None = None
    uptime_24h: float | None = None

    model_config = {"from_attributes": True}
