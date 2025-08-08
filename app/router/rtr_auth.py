"""Authentication router."""

from typing import Annotated

from app.dependencies.dep_auth import CurrentUserDep
from app.dependencies.dep_repos import UserRepDep
from app.schemas.sch_token import Token
from app.schemas.sch_user import UserRead
from app.service.hashcryp.serv_hasher import HasherService
from app.service.token.srv_token import create_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: UserRepDep,
) -> Token:
    """Login endpoint untuk mendapatkan access token."""
    user = user_repo.get_user_by_username(form_data.username)
    if not user or not HasherService.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token({"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: CurrentUserDep) -> UserRead:
    """Get current user information."""
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )
