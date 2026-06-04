from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CheckResponse(BaseModel):
    id: UUID
    endpoint_id: UUID
    status_code: int | None
    latency_ms: int
    is_up: bool
    error: str | None
    checked_at: datetime

    model_config = {"from_attributes": True}
