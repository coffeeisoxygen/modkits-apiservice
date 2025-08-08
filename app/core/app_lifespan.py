"""Application lifespan event handler for FastAPI.

Setup loguru logging and handle startup/shutdown events using lifespan context.
"""

import pathlib
from contextlib import asynccontextmanager

from app.dependencies.dep_settings import get_app_config, get_path_settings
from app.repos.rep_member import MemberRepository
from app.repos.rep_module import ModuleRepository
from app.repos.rep_user import UserRepository
from app.service.seeder.factory import seed_all_data
from app.service.watcher.srv_watcher import FileWatcher
from app.utils.log_setup import logger, setup_loguru

LEVEL = get_app_config().log_level
setup_loguru(level=LEVEL)

lifespan_logger = logger

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
    lifespan_logger.info("FastAPI application startup initiated")
    lifespan_logger.info("Seeding data files if not exist")

    try:
        seed_all_data(
            users_path=user_file_path,
            modules_path=module_file_path,
            members_path=member_file_path,
        )
        lifespan_logger.info("Data seeding completed successfully")
    except Exception as e:
        lifespan_logger.error(f"Data seeding failed: {e}")
        raise

    lifespan_logger.info("Registering repositories to app state")
    app.state.user_repo = user_repo
    app.state.module_repo = module_repo
    app.state.member_repo = member_repo
    lifespan_logger.info("All repositories registered to app state")

    lifespan_logger.info("Starting file watchers for data monitoring")
    user_watcher.start()
    module_watcher.start()
    member_watcher.start()
    app.state.user_watcher = user_watcher
    app.state.module_watcher = module_watcher
    app.state.member_watcher = member_watcher
    lifespan_logger.info("All file watchers started and registered to app state")
    lifespan_logger.info("FastAPI application startup completed successfully")

    try:
        yield
    finally:
        lifespan_logger.info("FastAPI application shutdown initiated")
        lifespan_logger.info("Stopping file watchers")
        try:
            user_watcher.stop()
        except Exception as e:
            lifespan_logger.error(f"Failed to stop user watcher: {e}")
        try:
            module_watcher.stop()
        except Exception as e:
            lifespan_logger.error(f"Failed to stop module watcher: {e}")
        try:
            member_watcher.stop()
        except Exception as e:
            lifespan_logger.error(f"Failed to stop member watcher: {e}")
        lifespan_logger.info("File watchers cleanup completed")
        lifespan_logger.info("FastAPI application shutdown completed")
