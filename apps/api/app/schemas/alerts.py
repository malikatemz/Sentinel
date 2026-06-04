from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: UUID
    endpoint_id: UUID
    type: str
    message: str
    notified: bool
    created_at: datetime
    endpoint_name: str | None = None

    model_config = {"from_attributes": True}
