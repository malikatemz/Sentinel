from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import PaginationParams, get_current_user, get_db
from ..models import Check, Endpoint, User
from ..schemas.endpoints import EndpointCreate, EndpointResponse, EndpointUpdate

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


@router.get("", response_model=list[EndpointResponse])
async def list_endpoints(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Endpoint)
        .where(Endpoint.user_id == user.id)
        .order_by(Endpoint.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    endpoints = result.scalars().all()

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)
    responses = []

    for ep in endpoints:
        # Latest check
        lc_result = await db.execute(
            select(Check)
            .where(Check.endpoint_id == ep.id)
            .order_by(Check.checked_at.desc())
            .limit(1)
        )
        lc = lc_result.scalar_one_or_none()

        # 24h uptime
        uptime_result = await db.execute(
            select(
                func.count(Check.id).label("total"),
                func.sum(case((Check.is_up == True, 1), else_=0)).label("up_count"),
            ).where(Check.endpoint_id == ep.id, Check.checked_at >= day_ago)
        )
        uptime_row = uptime_result.one()
        total = uptime_row.total or 0
        up = uptime_row.up_count or 0
        uptime = round((up / total * 100) if total > 0 else 100, 2)

        responses.append(EndpointResponse(
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
            uptime_24h=uptime,
        ))

    return responses


@router.post("", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    body: EndpointCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    endpoint = Endpoint(
        user_id=user.id,
        name=body.name,
        url=str(body.url),
        method=body.method,
        interval_seconds=body.interval_seconds,
        expected_status=body.expected_status,
    )
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)

    return EndpointResponse(
        id=endpoint.id,
        name=endpoint.name,
        url=str(endpoint.url),
        method=endpoint.method,
        interval_seconds=endpoint.interval_seconds,
        expected_status=endpoint.expected_status,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
    )


@router.patch("/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(
    endpoint_id: UUID,
    body: EndpointUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id, Endpoint.user_id == user.id)
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found.")

    update_data = body.model_dump(exclude_unset=True)
    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])
    for field, value in update_data.items():
        setattr(endpoint, field, value)

    await db.commit()
    await db.refresh(endpoint)

    return EndpointResponse(
        id=endpoint.id,
        name=endpoint.name,
        url=str(endpoint.url),
        method=endpoint.method,
        interval_seconds=endpoint.interval_seconds,
        expected_status=endpoint.expected_status,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
    )


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(
    endpoint_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id, Endpoint.user_id == user.id)
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found.")

    await db.delete(endpoint)
    await db.commit()
    return None
