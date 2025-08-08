"""Authentication dependencies."""

from typing import TYPE_CHECKING, Annotated

from app.schemas.sch_user import UserInDB
from app.service.token.srv_token import decode_access_token
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

if TYPE_CHECKING:
    from app.repos.rep_user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_user_repo_from_state(request: Request) -> "UserRepository":
    """Get UserRepository from app.state."""
    return request.app.state.user_repo


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated["UserRepository", Depends(get_user_repo_from_state)],
) -> UserInDB:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception

    username = payload["sub"]
    user = user_repo.get_user_by_username(username)
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserInDB:
    """Get current authenticated user that is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_admin_user(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> UserInDB:
    """Get current authenticated user that is active and admin (superuser)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# Type aliases for dependency injection
CurrentUserDep = Annotated[UserInDB, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[UserInDB, Depends(get_current_active_user)]
CurrentAdminUserDep = Annotated[UserInDB, Depends(get_current_admin_user)]
