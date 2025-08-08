"""wrapper to login the user."""

from app.router.management.rtr_admin import router as admin_router
from app.router.management.rtr_auth import router as auth_router

# from app.router.rtr_protected import router as protected_router
from app.router.management.rtr_user import router as user_router
from app.router.transaction.rtr_service_get import router as service_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(admin_router)
api_router.include_router(service_router)
# api_router.include_router(protected_router)

# # ...you can include more routers here as needed...
