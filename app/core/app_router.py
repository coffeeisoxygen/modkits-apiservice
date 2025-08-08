"""wrapper to login the user."""

from app.router.rtr_auth import router as auth_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth_router)

# # ...you can include more routers here as needed...
