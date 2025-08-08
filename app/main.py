import time

from app.core.app_exceptions import register_exception_handlers
from app.core.app_lifespan import app_lifespan
from app.core.app_middleware import LoggingMiddleware
from app.core.app_router import api_router
from app.dependencies.dep_auth import CurrentActiveUserDep
from app.utils.log_setup import logtrace_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Modkits API Service",
    version="1.0.0",
    description="API service for Modkits, providing essential functionalities.",
    lifespan=app_lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/", tags=["General"])
@logtrace_endpoint("root")
async def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to Modkits API Service!", "status": "ok"}


@app.get("/home", tags=["General"])
@logtrace_endpoint("home")
async def homepage(current_user: CurrentActiveUserDep) -> dict:
    """Homepage endpoint - requires authentication."""
    return {
        "message": f"Welcome home, {current_user.name}!",
        "user": {
            "username": current_user.username,
            "name": current_user.name,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
        },
        "quick_links": {
            "profile": "/user/profile",
            "dashboard": "/user/dashboard",
            "admin": "/adm/dashboard" if current_user.is_superuser else None,
        },
        "status": "authenticated",
    }


@app.get("/health", tags=["General"])
@logtrace_endpoint("health_check")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "service": "modkits-apiservice",
        "timestamp": time.time(),
    }
