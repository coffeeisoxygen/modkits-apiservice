# """Protected router examples untuk mendemonstrasikan dependency auth."""

# from app.dependencies.dep_auth import CurrentActiveUserDep, CurrentAdminUserDep
# from app.schemas.sch_user import UserRead
# from fastapi import APIRouter

# router = APIRouter(prefix="/protected", tags=["Protected"])


# @router.get("/user-only")
# async def user_only_endpoint(current_user: CurrentActiveUserDep) -> dict:
#     """Endpoint yang hanya butuh user login dan aktif.

#     Menggunakan CurrentActiveUserDep yang:
#     1. Cek token valid (get_current_user)
#     2. Cek user is_active = True (get_current_active_user)
#     """
#     return {
#         "message": "Hello authenticated active user!",
#         "user": {
#             "username": current_user.username,
#             "name": current_user.name,
#             "is_active": current_user.is_active,
#             "is_superuser": current_user.is_superuser,
#         },
#     }


# @router.get("/admin-only")
# async def admin_only_endpoint(current_user: CurrentAdminUserDep) -> dict:
#     """Endpoint yang butuh user admin dan aktif.

#     Menggunakan CurrentAdminUserDep yang:
#     1. Cek token valid (get_current_user)
#     2. Cek user is_active = True (get_current_active_user)
#     3. Cek user is_superuser = True (get_current_admin_user)
#     """
#     return {
#         "message": "Hello admin user!",
#         "user": {
#             "username": current_user.username,
#             "name": current_user.name,
#             "is_active": current_user.is_active,
#             "is_superuser": current_user.is_superuser,
#         },
#         "admin_data": {
#             "can_manage_users": True,
#             "can_access_admin_panel": True,
#         },
#     }


# @router.get("/user-profile", response_model=UserRead)
# async def get_user_profile(current_user: CurrentActiveUserDep) -> UserRead:
#     """Get user profile - butuh login dan aktif."""
#     return UserRead(
#         id=current_user.id,
#         username=current_user.username,
#         email=current_user.email,
#         name=current_user.name,
#         is_active=current_user.is_active,
#         is_superuser=current_user.is_superuser,
#     )


# @router.delete("/admin/delete-user/{user_id}")
# async def admin_delete_user(
#     user_id: str,
#     current_user: CurrentAdminUserDep,
# ) -> dict:
#     """Delete user - hanya admin yang bisa.

#     Contoh endpoint yang butuh admin privileges.
#     """
#     return {
#         "message": f"User {user_id} would be deleted by admin {current_user.username}",
#         "admin": current_user.username,
#         "action": "delete_user",
#         "target_user_id": user_id,
#     }
