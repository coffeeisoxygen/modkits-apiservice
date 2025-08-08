"""JWT and Token Related Setup."""

from pydantic import BaseModel, Field


class JwtConfig(BaseModel):
    """JWT configuration."""

    secret_key: str = Field(default="default-secret-key", alias="JWT__SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="JWT__ALGORITHM")


class TokenConfig(BaseModel):
    """Token configuration."""

    token_expiration_minutes: int = Field(default=60, alias="TOKEN__EXPIRATION_MINUTES")
