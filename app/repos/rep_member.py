from pathlib import Path
from typing import Any

import yaml
from app.core.exceptions import ValidationError, YamlReloadExceptionError
from app.dependencies.dep_settings import get_path_settings
from app.schemas.sch_member import MemberInDB
from app.utils.log_setup import logger

module_path: Path = get_path_settings()[0] / "members.yaml"


class MemberRepository:
    def __init__(self):
        logger.info("Initializing MemberRepository with path: %s", module_path)
        self.file_path = module_path
        self._members: list[MemberInDB] = []
        self.reload()

    def _load_data_from_file(self) -> list[MemberInDB]:
        """Memuat data dari file members.yaml dan memvalidasinya.

        Mengembalikan list objek MemberInDB atau list kosong jika file kosong.
        """
        operation_logger = logger.bind(operation="load_members_from_yaml")

        try:
            with open(self.file_path) as file:
                data: dict[str, list[dict[str, Any]]] = yaml.safe_load(file)
                if not data or "members" not in data:
                    operation_logger.warning(
                        "File members.yaml kosong atau tidak memiliki kunci 'members'."
                    )
                    return []

                # Memvalidasi setiap item dengan skema MemberInDB
                members_list = [
                    MemberInDB(**member_data) for member_data in data["members"]
                ]
                operation_logger.debug(
                    f"Berhasil memuat {len(members_list)} member dari file.",
                    members_loaded=len(members_list),
                )
                return members_list
        except (ValidationError, Exception) as e:
            operation_logger.error(
                "Gagal memuat atau memvalidasi file YAML.",
                file=self.file_path,
                exception=e,
            )
            # Melempar satu custom exception yang spesifik
            raise YamlReloadExceptionError(
                message="Terjadi kesalahan saat memuat atau memvalidasi file YAML.",
                context={"error_details": str(e)},
            ) from e

    def reload(self):
        """Memuat ulang semua data dari file dan memperbarui state internal."""
        logger.info("Memulai proses reload ModuleRepository.")
        try:
            self._modules = self._load_data_from_file()
            logger.info("ModuleRepository berhasil dimuat ulang.")
        except YamlReloadExceptionError as e:
            # Jika terjadi error saat memuat ulang, log tapi biarkan data lama tetap ada
            logger.bind(error=e.message, context=e.context).error(
                "Gagal memuat ulang data, menggunakan data lama."
            )
        except Exception as e:
            # Blok fallback untuk error tak terduga
            logger.bind(exception=str(e)).error(
                "Gagal memuat ulang data karena error tak terduga, menggunakan data lama."
            )

    def get_member_by_id(self, member_id: str) -> MemberInDB | None:
        """Mencari members di memori berdasarkan member_id."""
        for member in self._members:
            if member.member_id == member_id:
                logger.debug("Member ditemukan.", member_id=member_id)
                return member
        logger.warning("Member tidak ditemukan.", member_id=member_id)
        return None

    def get_all_members(self) -> list[MemberInDB]:
        """Mengembalikan semua member yang ada."""
        return self._members
