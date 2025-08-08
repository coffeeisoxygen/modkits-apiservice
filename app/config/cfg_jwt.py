"""JWT and Token Related Setup."""

from pydantic import BaseModel, Field


class JwtConfig(BaseModel):
    """JWT configuration."""

    secret_key: str = Field(default="default-secret-key")
    algorithm: str = Field(default="HS256")


class TokenConfig(BaseModel):
    """Token configuration."""

    expiration_minutes: int = 60
