"""Signature service dependencies."""

from typing import Annotated

from app.service.signature.srv_signature import OtomaxSignatureService
from fastapi import Depends


def get_signature_service() -> OtomaxSignatureService:
    """Get signature service instance.

    Returns:
        OtomaxSignatureService: Instance of signature service
    """
    return OtomaxSignatureService()


# Type alias for dependency injection
SignatureServiceDep = Annotated[OtomaxSignatureService, Depends(get_signature_service)]
