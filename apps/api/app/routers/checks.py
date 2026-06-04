from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import PaginationParams, get_current_user, get_db
from ..models import Check, Endpoint, User
from ..schemas.checks import CheckResponse

router = APIRouter(tags=["checks"])


@router.get("/endpoints/{endpoint_id}/checks", response_model=list[CheckResponse])
async def list_checks(
    endpoint_id: UUID,
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify endpoint ownership
    ep_result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id, Endpoint.user_id == user.id)
    )
    if not ep_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found.")

    result = await db.execute(
        select(Check)
        .where(Check.endpoint_id == endpoint_id)
        .order_by(Check.checked_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    return result.scalars().all()
