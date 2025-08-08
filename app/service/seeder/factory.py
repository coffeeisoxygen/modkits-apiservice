import pathlib
import uuid
from datetime import datetime

import yaml
from app.core.exceptions import PathResolverError
from app.schemas.sch_member import MemberInDB
from app.schemas.sch_module import ModuleInDB
from app.schemas.sch_user import UserInDB
from app.service.hashcryp.serv_hasher import HasherService
from app.utils.log_setup import logger

DEFAULT_USERS = [
    {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "password": "admin123",
        "name": "Administrator",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
    },
    {
        "id": str(uuid.uuid4()),
        "username": "user1",
        "password": "user123",
        "name": "User One",
        "email": "user1@example.com",
        "is_active": True,
        "is_superuser": False,
    },
]


DEFAULT_MODULES = [
    {
        "moduleid": "digiposwr",
        "provider": "digipos",  # gunakan string sesuai value EnumAPIProvider
        "username": "sample_user",
        "pin": "1234",
        "password": "sample_pass",
        "msisdn": "081234567890",
        "email": "sample@example.com",
        "base_url": "https://api.example.com",
        "is_active": True,
        "name": "Sample Module",
        "description": "Sample module for testing",
    }
]


DEFAULT_MEMBERS = [
    {
        "member_id": "mem_001",
        "pin": "1234",
        "password": "member123",
        "is_active": True,
        "ip_address": "192.168.1.100",
        "report_url": "https://api.example.com/reports/mem_001",
        "allow_nosign": False,
    },
    {
        "member_id": "mem_002",
        "pin": "5678",
        "password": "member456",
        "is_active": True,
        "ip_address": "192.168.1.101",
        "report_url": "https://api.example.com/reports/mem_002",
        "allow_nosign": True,
    },
]
# Create exclusive logger for seeding operations
seeder_logger = logger.bind(
    component="seeder", operation="data_seeding", context="application_bootstrap"
)


def _ensure_parent_dir(path: pathlib.Path) -> None:
    """Ensure parent directory exists for the given path."""
    log = seeder_logger.bind(operation="ensure_parent_dir", path=str(path))
    if not path.parent.exists():
        try:
            log.info("Creating parent directory: {}", path.parent)
            path.parent.mkdir(parents=True, exist_ok=True)
            log.success("Parent directory created successfully")
        except Exception as e:
            log.error(
                "Failed to create parent directory",
                error=str(e),
                path=str(path),
                parent=str(path.parent),
            )
            raise PathResolverError(
                str(e), context={"path": str(path), "parent": str(path.parent)}
            ) from e
    else:
        log.debug("Parent directory already exists")


def seed_users(file_path: pathlib.Path) -> None:
    """Seed users file with default admin if not exists or empty."""
    log = seeder_logger.bind(operation="seed_users", path=str(file_path))
    log.info("Starting user seeding process")

    if not file_path.exists() or file_path.stat().st_size == 0:
        _ensure_parent_dir(file_path)
        users = []
        for user in DEFAULT_USERS:
            user_obj = UserInDB(**user)
            user_dict = user_obj.model_dump()
            user_dict["password"] = HasherService.hash_password(user_dict["password"])
            users.append(user_dict)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"users": users}, f, sort_keys=False, default_flow_style=False
                )
            log.success("Seeded users file successfully", users_count=len(users))
        except Exception as e:
            log.error(
                "Failed to write users file",
                error=str(e),
                path=str(file_path),
            )
            raise PathResolverError(str(e), context={"path": str(file_path)}) from e
    else:
        log.debug("Users file already exists and is not empty")


def seed_modules(file_path: pathlib.Path) -> None:
    """Seed modules file with default modules if not exists or empty."""
    log = seeder_logger.bind(operation="seed_modules", path=str(file_path))
    log.info("Starting module seeding process")

    if not file_path.exists() or file_path.stat().st_size == 0:
        _ensure_parent_dir(file_path)
        modules = []
        for module in DEFAULT_MODULES:
            module_obj = ModuleInDB(
                **module,
                created_at=datetime.now(),
            )
            module_dict = module_obj.model_dump()
            # Convert SecretStr fields to plain string for YAML
            for key in ["username", "pin", "password"]:
                if key in module_dict and hasattr(module_dict[key], "get_secret_value"):
                    module_dict[key] = module_dict[key].get_secret_value()
            # Convert AnyHttpUrl and EmailStr to string for YAML
            if "base_url" in module_dict and hasattr(
                module_dict["base_url"], "__str__"
            ):
                module_dict["base_url"] = str(module_dict["base_url"])
            if "email" in module_dict and hasattr(module_dict["email"], "__str__"):
                module_dict["email"] = str(module_dict["email"])
            modules.append(module_dict)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"modules": modules},
                    f,
                    sort_keys=False,
                    default_flow_style=False,
                )
            log.success("Seeded modules file successfully", modules_count=len(modules))
        except Exception as e:
            log.error(
                "Failed to write modules file",
                error=str(e),
                path=str(file_path),
            )
            raise PathResolverError(str(e), context={"path": str(file_path)}) from e
    else:
        log.debug("Modules file already exists and is not empty")


def seed_members(file_path: pathlib.Path) -> None:
    """Seed members file with default members if not exists or empty."""
    log = seeder_logger.bind(operation="seed_members", path=str(file_path))
    log.info("Starting member seeding process")

    if not file_path.exists() or file_path.stat().st_size == 0:
        _ensure_parent_dir(file_path)
        members = []
        for member in DEFAULT_MEMBERS:
            # Create MemberInDB object for validation
            member_obj = MemberInDB(**member)
            member_dict = member_obj.model_dump()

            # Keep pin and password as plain text for members
            # They will be exposed in GET requests when allow_nosign=true
            member_dict["password"] = member_dict["password"].get_secret_value()
            member_dict["pin"] = member_dict["pin"].get_secret_value()
            # Convert AnyHttpUrl to string for YAML
            if "report_url" in member_dict and hasattr(
                member_dict["report_url"], "__str__"
            ):
                member_dict["report_url"] = str(member_dict["report_url"])

            members.append(member_dict)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"members": members},
                    f,
                    sort_keys=False,
                    default_flow_style=False,
                )
            log.success("Seeded members file successfully", members_count=len(members))
        except Exception as e:
            log.error(
                "Failed to write members file",
                error=str(e),
                path=str(file_path),
            )
            raise PathResolverError(str(e), context={"path": str(file_path)}) from e
    else:
        log.debug("Members file already exists and is not empty")


def seed_all_data(
    users_path: pathlib.Path,
    modules_path: pathlib.Path,
    members_path: pathlib.Path,
) -> None:
    """Seed all data files with default values if they don't exist or are empty."""
    log = seeder_logger.bind(operation="seed_all_data")
    log.info("🌱 Starting complete data seeding process")

    try:
        seed_users(users_path)
        seed_modules(modules_path)
        seed_members(members_path)
        log.success("🎉 All data seeding completed successfully")
    except Exception as e:
        log.error("Data seeding failed", error=str(e))
        raise
