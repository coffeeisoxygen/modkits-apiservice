"""Example router showing how to use authentication dependencies."""

from app.dependencies.dep_auth import CurrentActiveUserDep, CurrentAdminUserDep
from app.schemas.sch_user import UserRead
from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["Example"])


@router.get("/protected")
async def protected_endpoint(current_user: CurrentActiveUserDep) -> dict:
    """Endpoint yang memerlukan user login dan aktif."""
    return {
        "message": "This is a protected endpoint",
        "user": current_user.username,
        "is_active": current_user.is_active,
    }


@router.get("/admin-only")
async def admin_only_endpoint(current_user: CurrentAdminUserDep) -> dict:
    """Endpoint yang memerlukan user admin dan aktif."""
    return {
        "message": "This is an admin-only endpoint",
        "user": current_user.username,
        "is_admin": current_user.is_superuser,
        "is_active": current_user.is_active,
    }


@router.get("/user-info")
async def get_user_info(current_user: CurrentActiveUserDep) -> UserRead:
    """Get user information - requires active user."""
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )
