"""token related services."""

from datetime import datetime, timedelta

import jwt
from app.dependencies.dep_settings import get_jwt_config, get_token_config
from loguru import logger

SECRET_KEY = get_jwt_config().secret_key
ALGORITHM = get_jwt_config().algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = get_token_config().expiration_minutes

# Bind logger for token service
token_logger = logger.bind(service="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token_logger.debug("Creating access token", data=data, expire=expire)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    token_logger.debug("Access token created", token=encoded_jwt)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode a JWT access token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_logger.debug("Access token decoded", payload=payload)
        return payload
    except jwt.PyJWTError as e:
        token_logger.warning("Failed to decode access token", error=str(e), token=token)
        return None
