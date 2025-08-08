from typing import Annotated

from app.repos.rep_member import MemberRepository
from app.repos.rep_module import ModuleRepository
from app.repos.rep_user import UserRepository
from fastapi import Depends, Request


def get_module_repo(request: Request):
    """Ambil ModuleRepository dari app.state."""
    return request.app.state.module_repo


def get_user_repo(request: Request):
    """Ambil UserRepository dari app.state."""
    return request.app.state.user_repo


def get_member_repo(request: Request):
    """Ambil MemberRepository dari app.state."""
    return request.app.state.member_repo


# Anotasi biar gampang nge load

MemberRepDep = Annotated[MemberRepository, Depends(get_member_repo)]
UserRepDep = Annotated[UserRepository, Depends(get_user_repo)]
ModuleRepDep = Annotated[ModuleRepository, Depends(get_module_repo)]
