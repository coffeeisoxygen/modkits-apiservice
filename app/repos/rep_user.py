from pathlib import Path
from typing import Any

import yaml
from app.core.exceptions import ValidationError, YamlReloadExceptionError
from app.dependencies.dep_settings import get_path_settings
from app.schemas.sch_user import UserInDB
from app.utils.log_setup import logger


class UserRepository:
    def __init__(self, file_path: Path | None = None):
        """Initialize UserRepository with optional file path.

        Args:
            file_path: Path to users.yaml file. If None, uses default path from settings.
        """
        if file_path is None:
            file_path = get_path_settings()[0] / "users.yaml"

        logger.info("Initializing UserRepository with path: %s", file_path)
        self.file_path = file_path
        self._users: list[UserInDB] = []
        self.reload()

    def _load_data_from_file(self) -> list[UserInDB]:
        operation_logger = logger.bind(operation="load_users_from_yaml")
        try:
            with open(self.file_path) as file:
                data: dict[str, list[dict[str, Any]]] = yaml.safe_load(file)
                if not data or "users" not in data:
                    return []
                users_list = [UserInDB(**user_data) for user_data in data["users"]]
                operation_logger.debug(
                    f"Successfully loaded {len(users_list)} users.",
                    users_loaded=len(users_list),
                )
                return users_list
        except (ValidationError, Exception) as e:
            operation_logger.error(
                "Failed to load or validate YAML file.",
                file=self.file_path,
                exception=e,
            )
            raise YamlReloadExceptionError(
                message="An error occurred while loading or validating the YAML file.",
                context={"error_details": str(e)},
            ) from e

    def reload(self):
        logger.info("Starting UserRepository reload process.")
        try:
            self._users = self._load_data_from_file()
            logger.info("UserRepository successfully reloaded.")
        except YamlReloadExceptionError as e:
            logger.error(
                "Failed to reload data, using old data.",
                error=e.message,
                context=e.context,
            )
        except Exception as e:
            logger.error(
                "Failed to reload data due to unexpected error, using old data.",
                exception=e,
            )

    def get_user_by_username(self, username: str) -> UserInDB | None:
        for user in self._users:
            if user.username == username:
                logger.debug("User found.", user=username)
                return user
        logger.warning("User not found.", user=username)
        return None

    def get_all_users(self) -> list[UserInDB]:
        return self._users

    def get_user_by_id(self, user_id: str) -> UserInDB | None:
        for user in self._users:
            if user.id == user_id:
                logger.debug("User found by ID.", user_id=user_id)
                return user
        logger.warning("User not found by ID.", user_id=user_id)
        return None
