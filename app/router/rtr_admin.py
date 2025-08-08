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
from app.dependencies.dep_repos import ModuleRepDep
from app.dependencies.dep_settings import (
    AppConfigDep,
    JwtConfigDep,
    TokenConfigDep,
)
from app.schemas.sch_module import ModuleInDB
from app.utils.log_setup import logger, logtrace_endpoint
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])


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
