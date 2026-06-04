from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import PaginationParams, get_current_user, get_db
from ..models import Alert, Endpoint, User
from ..schemas.alerts import AlertResponse
from ..services.email_service import send_test_alert_email

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get user's endpoint IDs
    ep_result = await db.execute(
        select(Endpoint.id).where(Endpoint.user_id == user.id)
    )
    endpoint_ids = [row[0] for row in ep_result.all()]

    if not endpoint_ids:
        return []

    result = await db.execute(
        select(Alert, Endpoint.name.label("endpoint_name"))
        .join(Endpoint, Alert.endpoint_id == Endpoint.id)
        .where(Alert.endpoint_id.in_(endpoint_ids))
        .order_by(Alert.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )

    alerts = []
    for row in result.all():
        alert = row[0]
        alerts.append(AlertResponse(
            id=alert.id,
            endpoint_id=alert.endpoint_id,
            type=alert.type,
            message=alert.message,
            notified=alert.notified,
            created_at=alert.created_at,
            endpoint_name=row.endpoint_name,
        ))
    return alerts


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_alert(user: User = Depends(get_current_user)):
    sent = await send_test_alert_email(user.email)
    if not sent:
        return {"status": "skipped", "message": "SMTP is not configured. Set SMTP_USER and SMTP_PASSWORD in .env."}
    return {"status": "sent", "message": f"Test alert sent to {user.email}."}
