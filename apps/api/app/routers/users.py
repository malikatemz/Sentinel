from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..models import User
from ..schemas.auth import UserResponse

router = APIRouter(tags=["users"])


@router.get("/user", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
