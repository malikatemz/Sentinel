from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Alert, Check, Endpoint
from ..schemas.dashboard import DashboardResponse, ResponseDataPoint, SummaryCards


async def get_dashboard(db: AsyncSession, user_id: UUID) -> DashboardResponse:
    """Build aggregated dashboard data for the user."""
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    # Get all user endpoints
    result = await db.execute(
        select(Endpoint).where(Endpoint.user_id == user_id).order_by(Endpoint.created_at.desc())
    )
    endpoints = result.scalars().all()

    if not endpoints:
        return DashboardResponse(summary=SummaryCards())

    endpoint_ids = [e.id for e in endpoints]

    # Latest check per endpoint (subquery for is_up status)
    latest_checks_sub = (
        select(
            Check.endpoint_id,
            Check.is_up,
            Check.status_code,
            Check.checked_at,
            func.row_number().over(partition_by=Check.endpoint_id, order_by=Check.checked_at.desc()).label("rn"),
        )
        .where(Check.endpoint_id.in_(endpoint_ids))
        .subquery()
    )

    latest_result = await db.execute(
        select(latest_checks_sub).where(latest_checks_sub.c.rn == 1)
    )
    latest_checks = {row.endpoint_id: row for row in latest_result.all()}

    # Avg response time (last 24h)
    avg_result = await db.execute(
        select(func.avg(Check.latency_ms)).where(
            Check.endpoint_id.in_(endpoint_ids),
            Check.checked_at >= day_ago,
        )
    )
    avg_response = avg_result.scalar() or 0

    # Alerts in last 24h
    alerts_count_result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.endpoint_id.in_(endpoint_ids),
            Alert.created_at >= day_ago,
        )
    )
    alerts_24h = alerts_count_result.scalar() or 0

    # Uptime (last 24h) — fraction of checks where is_up=True
    uptime_result = await db.execute(
        select(
            func.count(Check.id).label("total"),
            func.sum(case((Check.is_up == True, 1), else_=0)).label("up_count"),
        ).where(
            Check.endpoint_id.in_(endpoint_ids),
            Check.checked_at >= day_ago,
        )
    )
    uptime_row = uptime_result.one()
    total_checks = uptime_row.total or 0
    up_checks = uptime_row.up_count or 0
    overall_uptime = round((up_checks / total_checks * 100) if total_checks > 0 else 100, 2)

    # Count up / down
    up_count = sum(1 for e in endpoints if e.id in latest_checks and latest_checks[e.id].is_up)
    down_count = sum(1 for e in endpoints if e.id in latest_checks and not latest_checks[e.id].is_up)

    summary = SummaryCards(
        total_endpoints=len(endpoints),
        endpoints_up=up_count,
        endpoints_down=down_count,
        avg_response_ms=round(avg_response, 1),
        total_alerts_24h=alerts_24h,
        overall_uptime=overall_uptime,
    )

    # Recent alerts
    alerts_result = await db.execute(
        select(Alert, Endpoint.name.label("endpoint_name"))
        .join(Endpoint, Alert.endpoint_id == Endpoint.id)
        .where(Alert.endpoint_id.in_(endpoint_ids))
        .order_by(Alert.created_at.desc())
        .limit(10)
    )
    recent_alerts = []
    for row in alerts_result.all():
        alert = row[0]
        recent_alerts.append({
            "id": alert.id,
            "endpoint_id": alert.endpoint_id,
            "type": alert.type,
            "message": alert.message,
            "notified": alert.notified,
            "created_at": alert.created_at,
            "endpoint_name": row.endpoint_name,
        })

    # Response history (last 50 checks across all endpoints)
    history_result = await db.execute(
        select(Check.checked_at, Check.latency_ms, Endpoint.name.label("endpoint_name"))
        .join(Endpoint, Check.endpoint_id == Endpoint.id)
        .where(Check.endpoint_id.in_(endpoint_ids))
        .order_by(Check.checked_at.desc())
        .limit(50)
    )
    response_history = [
        ResponseDataPoint(checked_at=row.checked_at, latency_ms=row.latency_ms, endpoint_name=row.endpoint_name)
        for row in history_result.all()
    ]

    # Build endpoint responses with latest check info
    from ..schemas.endpoints import EndpointResponse

    endpoint_responses = []
    for ep in endpoints:
        lc = latest_checks.get(ep.id)

        # Calculate 24h uptime for this endpoint
        ep_uptime_result = await db.execute(
            select(
                func.count(Check.id).label("total"),
                func.sum(case((Check.is_up == True, 1), else_=0)).label("up_count"),
            ).where(Check.endpoint_id == ep.id, Check.checked_at >= day_ago)
        )
        ep_uptime_row = ep_uptime_result.one()
        ep_total = ep_uptime_row.total or 0
        ep_up = ep_uptime_row.up_count or 0
        ep_uptime = round((ep_up / ep_total * 100) if ep_total > 0 else 100, 2)

        endpoint_responses.append(EndpointResponse(
            id=ep.id,
            name=ep.name,
            url=str(ep.url),
            method=ep.method,
            interval_seconds=ep.interval_seconds,
            expected_status=ep.expected_status,
            is_active=ep.is_active,
            created_at=ep.created_at,
            updated_at=ep.updated_at,
            last_check_at=lc.checked_at if lc else None,
            last_status=lc.status_code if lc else None,
            is_up=lc.is_up if lc else None,
            uptime_24h=ep_uptime,
        ))

    return DashboardResponse(
        summary=summary,
        recent_alerts=recent_alerts,
        endpoints=endpoint_responses,
        response_history=response_history,
    )
