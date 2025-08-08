"""User router untuk endpoint yang butuh user login + active."""

from app.dependencies.dep_auth import CurrentActiveUserDep
from app.schemas.sch_user import UserRead, UserUpdate
from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserRead)
async def get_user_profile(current_user: CurrentActiveUserDep) -> UserRead:
    """Get current user profile."""
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )


@router.put("/profile", response_model=UserRead)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: CurrentActiveUserDep,
) -> UserRead:
    """Update current user profile."""
    # Disini nanti implementasi update di repository
    # Untuk sekarang return data yang sudah ada dengan update
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=user_update.email or current_user.email,
        name=user_update.name or current_user.name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )


@router.get("/dashboard")
async def get_user_dashboard(current_user: CurrentActiveUserDep) -> dict:
    """Get user dashboard data."""
    return {
        "message": f"Welcome to your dashboard, {current_user.name}!",
        "user": {
            "username": current_user.username,
            "name": current_user.name,
            "is_active": current_user.is_active,
        },
        "stats": {
            "login_count": 42,  # Placeholder data
            "last_login": "2025-08-08T12:00:00Z",
        },
    }


@router.get("/settings")
async def get_user_settings(current_user: CurrentActiveUserDep) -> dict:
    """Get user settings."""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True,
        },
        "security": {
            "two_factor_enabled": False,
            "last_password_change": "2025-01-01T00:00:00Z",
        },
    }
