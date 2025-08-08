"""Application lifespan event handler for FastAPI.

Setup loguru logging and handle startup/shutdown events using lifespan context.
"""

import pathlib
from contextlib import asynccontextmanager

from app.dependencies.dep_settings import get_app_config, get_path_settings
from app.repos.rep_member import MemberRepository
from app.repos.rep_module import ModuleRepository
from app.repos.rep_user import UserRepository
from app.service.watcher.srv_watcher import FileWatcher
from app.utils.log_setup import logger, setup_loguru

LEVEL = get_app_config().log_level
setup_loguru(level=LEVEL)

# Create exclusive logger for lifespan operations
lifespan_logger = logger.bind(
    component="lifespan", operation="app_startup_shutdown", context="fastapi_lifecycle"
)

# Get paths from settings
data_path = get_path_settings()[0]
user_file_path: pathlib.Path = data_path / "users.yaml"
module_file_path: pathlib.Path = data_path / "modules.yaml"
member_file_path: pathlib.Path = data_path / "members.yaml"

# Initialize repositories with injected paths
user_repo = UserRepository(file_path=user_file_path)
module_repo = ModuleRepository(file_path=module_file_path)
member_repo = MemberRepository(file_path=member_file_path)

# Create watchers with proper file paths and callbacks
user_watcher = FileWatcher(file_path=user_file_path, callback=user_repo.reload)
module_watcher = FileWatcher(file_path=module_file_path, callback=module_repo.reload)
member_watcher = FileWatcher(file_path=member_file_path, callback=member_repo.reload)


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, RUF029
    """Lifespan context for FastAPI app: setup logging and log events."""
    lifespan_logger.info("🚀 FastAPI application startup initiated")

    # Task 1: Register repositories to app state
    startup_logger = lifespan_logger.bind(task="repository_registration")
    startup_logger.info("Starting repository registration to app state")

    app.state.user_repo = user_repo
    startup_logger.debug("UserRepository registered to app.state")

    app.state.module_repo = module_repo
    startup_logger.debug("ModuleRepository registered to app.state")

    app.state.member_repo = member_repo
    startup_logger.debug("MemberRepository registered to app.state")

    startup_logger.success("All repositories successfully registered to app state")

    # Task 2: Start file watchers
    watcher_logger = lifespan_logger.bind(task="file_watcher_startup")
    watcher_logger.info("Starting file watchers for data monitoring")

    user_watcher.start()
    watcher_logger.debug("User file watcher started", file_path=str(user_file_path))

    module_watcher.start()
    watcher_logger.debug("Module file watcher started", file_path=str(module_file_path))

    member_watcher.start()
    watcher_logger.debug("Member file watcher started", file_path=str(member_file_path))

    # Register watchers to app state
    app.state.user_watcher = user_watcher
    app.state.module_watcher = module_watcher
    app.state.member_watcher = member_watcher

    watcher_logger.success("All file watchers started and registered to app state")
    lifespan_logger.success("🎉 FastAPI application startup completed successfully")

    try:
        yield
    finally:
        # Shutdown process
        shutdown_logger = lifespan_logger.bind(task="application_shutdown")
        shutdown_logger.info("🛑 FastAPI application shutdown initiated")

        # Stop watchers
        watcher_shutdown_logger = shutdown_logger.bind(subtask="watcher_cleanup")
        watcher_shutdown_logger.info("Stopping file watchers")

        try:
            user_watcher.stop()
            watcher_shutdown_logger.debug("User file watcher stopped")
        except Exception as e:
            watcher_shutdown_logger.error("Failed to stop user watcher", error=str(e))

        try:
            module_watcher.stop()
            watcher_shutdown_logger.debug("Module file watcher stopped")
        except Exception as e:
            watcher_shutdown_logger.error("Failed to stop module watcher", error=str(e))

        try:
            member_watcher.stop()
            watcher_shutdown_logger.debug("Member file watcher stopped")
        except Exception as e:
            watcher_shutdown_logger.error("Failed to stop member watcher", error=str(e))

        watcher_shutdown_logger.success("File watchers cleanup completed")
        shutdown_logger.success("🏁 FastAPI application shutdown completed")
