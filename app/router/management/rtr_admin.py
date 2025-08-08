"""Admin router untuk endpoint yang butuh admin privileges."""

import time

from app.dependencies.dep_auth import CurrentAdminUserDep
from app.dependencies.dep_context import (
    ClientIpDep,
    MethodDep,
    PathDep,
    RequestIdDep,
    UserAgentDep,
)
from app.dependencies.dep_repos import ModuleRepDep, UserRepDep
from app.dependencies.dep_settings import (
    AppConfigDep,
    JwtConfigDep,
    TokenConfigDep,
)
from app.schemas.sch_module import ModuleInDB
from app.schemas.sch_user import UserCreate, UserRead, UserReadList, UserUpdate
from app.utils.log_setup import logger, logtrace_endpoint
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/adm", tags=["Admin"])


@router.get("/dashboard")
async def get_admin_dashboard(current_user: CurrentAdminUserDep) -> dict:
    """Admin dashboard - Overview semua sistem."""
    return {
        "message": f"Welcome to admin dashboard, {current_user.name}!",
        "admin": {
            "username": current_user.username,
            "name": current_user.name,
            "is_superuser": current_user.is_superuser,
        },
        "system_stats": {
            "total_users": 10,  # Placeholder
            "active_users": 8,
            "total_modules": 5,
            "system_uptime": "2 days, 5 hours",
        },
    }


@router.get("/info")
@logtrace_endpoint("admin_app_info")
async def get_admin_app_info(
    current_user: CurrentAdminUserDep,
    app_config: AppConfigDep,
    jwt_config: JwtConfigDep,
    token_config: TokenConfigDep,
) -> dict:
    """Get application configuration information - Admin only."""
    environments_info = {
        "app": app_config,
        "jwt": jwt_config,
        "token": token_config,
        "accessed_by": {
            "username": current_user.username,
            "name": current_user.name,
        },
    }
    return environments_info


@router.get("/modules")
async def list_admin_modules(
    current_user: CurrentAdminUserDep,
    module_repo: ModuleRepDep,
) -> list[ModuleInDB]:
    """List semua data module dari repository - Admin only."""
    _ = current_user  # Suppress unused warning - used for auth
    return module_repo.get_all_modules()


@router.get("/test-sensitive")
@logtrace_endpoint("admin_test_sensitive")
async def admin_test_sensitive_data(current_user: CurrentAdminUserDep):
    """Test endpoint for sensitive data redaction - Admin only."""
    logger.info("Admin testing sensitive data logging:")
    logger.info("User password: mySecretPassword123")
    logger.info("API key: sk-1234567890abcdef")
    logger.info("Email: john.doe@company.com")
    logger.info("Phone: +628123456789")
    logger.info("Credit Card: 4532-1234-5678-9012")
    logger.info("Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    logger.info(
        "Secret key in JSON: {'secret': 'top-secret-data', 'public': 'visible'}"
    )

    return {
        "status": "admin test completed",
        "message": "Check logs to see sensitive data redaction in action",
        "tested_by": {
            "username": current_user.username,
            "name": current_user.name,
        },
    }


@router.get("/whoami")
@logtrace_endpoint("admin_whoami")
async def admin_whoami(
    current_user: CurrentAdminUserDep,
    request_id: RequestIdDep,
    client_ip: ClientIpDep,
    user_agent: UserAgentDep,
    path: PathDep,
    method: MethodDep,
):
    """Show current request context for admin - Admin only."""
    return {
        "admin_info": {
            "username": current_user.username,
            "name": current_user.name,
            "is_superuser": current_user.is_superuser,
        },
        "request_context": {
            "request_id": request_id,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "path": path,
            "method": method,
        },
    }


@router.get("/system-status")
async def get_system_status(current_user: CurrentAdminUserDep):
    """Get system status - Admin only."""
    return {
        "status": "operational",
        "service": "modkits-apiservice",
        "timestamp": time.time(),
        "admin_access": True,
        "checked_by": {
            "username": current_user.username,
            "name": current_user.name,
        },
    }


@router.get("/users", response_model=UserReadList)
async def list_users(
    current_user: CurrentAdminUserDep,
    user_repo: UserRepDep,
) -> UserReadList:
    """List all users - Admin only."""
    users = user_repo.get_all_users()
    user_reads = [
        UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
        for user in users
    ]
    return UserReadList(users=user_reads, total=len(user_reads))


@router.post("/users", response_model=UserRead)
async def create_user(
    user_create: UserCreate,
    current_user: CurrentAdminUserDep,
    user_repo: UserRepDep,
) -> UserRead:
    """Create new user - Admin only."""
    # Placeholder implementation - nanti implementasi di repository
    return UserRead(
        id="new-user-id",
        username=user_create.username,
        email=user_create.email,
        name=user_create.name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
    )


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: str,
    current_user: CurrentAdminUserDep,
    user_repo: UserRepDep,
) -> UserRead:
    """Get specific user by ID - Admin only."""
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: CurrentAdminUserDep,
    user_repo: UserRepDep,
) -> UserRead:
    """Update specific user - Admin only."""
    user = user_repo.get_user_by_id(user_id)
    if not user:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Placeholder implementation - nanti implementasi update di repository
    return UserRead(
        id=user.id,
        username=user_update.username or user.username,
        email=user_update.email or user.email,
        name=user_update.name or user.name,
        is_active=user_update.is_active
        if user_update.is_active is not None
        else user.is_active,
        is_superuser=user_update.is_superuser
        if user_update.is_superuser is not None
        else user.is_superuser,
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: CurrentAdminUserDep,
    user_repo: UserRepDep,
) -> dict:
    """Delete specific user - Admin only."""
    user = user_repo.get_user_by_id(user_id)
    if not user:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Prevent self-deletion
    if user.username == current_user.username:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Placeholder implementation - nanti implementasi delete di repository
    return {
        "message": f"User {user.username} (ID: {user_id}) would be deleted",
        "deleted_by": current_user.username,
        "action": "delete_user",
        "target_user": {
            "id": user_id,
            "username": user.username,
            "name": user.name,
        },
    }
