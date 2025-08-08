"""Service request/response schemas using Pydantic V2."""

from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator


class ServiceRequest(BaseModel):
    """Schema untuk incoming service request dari OtomaX.

    Example request:
    product=CLPDATA&qty=1&dest=081295221639&refid=3040881&memberid=vps&sign=MsP6Aticed6s1rlEhvj4NKceFVQ
    """

    product: str = Field(..., description="Product code", min_length=1, max_length=50)
    qty: int = Field(default=1, description="Quantity", ge=1, le=1000)
    dest: str = Field(
        ..., description="Destination (phone number)", min_length=10, max_length=15
    )
    refid: str = Field(
        ..., description="Reference/Transaction ID", min_length=1, max_length=50
    )
    memberid: str = Field(..., description="Member ID", min_length=1, max_length=50)
    sign: str | None = Field(
        None, description="Signature for verification", max_length=100
    )

    @field_validator("dest")
    @classmethod
    def validate_dest(cls, v: str) -> str:
        """Validate destination phone number format."""
        # Remove any non-digit characters for validation
        cleaned = "".join(filter(str.isdigit, v))
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Destination must be 10-15 digits")
        return v

    @field_validator("product")
    @classmethod
    def validate_product(cls, v: str) -> str:
        """Validate product code format."""
        if not v.strip():
            raise ValueError("Product code cannot be empty")
        return v.strip().upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "product": "CLPDATA",
                "qty": 1,
                "dest": "081295221639",
                "refid": "3040881",
                "memberid": "vps",
                "sign": "MsP6Aticed6s1rlEhvj4NKceFVQ",
            }
        }
    }


class MemberCredentials(BaseModel):
    """Schema untuk member credentials validation."""

    memberid: str = Field(..., description="Member ID", min_length=1, max_length=50)
    pin: str = Field(..., description="Member PIN", min_length=4, max_length=10)
    password: str = Field(
        ..., description="Member password", min_length=6, max_length=100
    )

    model_config = {
        "json_schema_extra": {
            "example": {"memberid": "vps", "pin": "777999", "password": "vps777999"}
        }
    }


class ServiceResponse(BaseModel):
    """Schema untuk service response ke OtomaX."""

    status: str = Field(
        ..., description="Response status", pattern="^(success|error|pending)$"
    )
    message: str = Field(..., description="Response message")
    refid: str = Field(..., description="Reference/Transaction ID")
    data: dict[str, Any] | None = Field(None, description="Additional response data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "message": "Transaction processed successfully",
                "refid": "3040881",
                "data": {"sn": "1234567890", "balance": 95000, "customer": "John Doe"},
            }
        }
    }


class ErrorResponse(BaseModel):
    """Schema untuk error response."""

    status: str = Field(default="error", description="Response status")
    message: str = Field(..., description="Error message")
    refid: str | None = Field(None, description="Reference ID if available")
    error_code: str | None = Field(None, description="Specific error code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "message": "Invalid signature",
                "refid": "3040881",
                "error_code": "INVALID_SIGNATURE",
            }
        }
    }


class SignatureValidationRequest(BaseModel):
    """Schema untuk signature validation request."""

    memberid: str = Field(..., description="Member ID")
    product: str = Field(..., description="Product code")
    dest: str = Field(..., description="Destination")
    refid: str = Field(..., description="Reference ID")
    pin: str = Field(..., description="Member PIN")
    password: str = Field(..., description="Member password")
    sign: str = Field(..., description="Signature to validate")

    model_config = {
        "json_schema_extra": {
            "example": {
                "memberid": "vps",
                "product": "CLPDATA",
                "dest": "081295221639",
                "refid": "3040881",
                "pin": "777999",
                "password": "vps777999",
                "sign": "MsP6Aticed6s1rlEhvj4NKceFVQ",
            }
        }
    }


# Type aliases for better readability
ServiceRequestType = Annotated[
    ServiceRequest, Field(description="Service request from OtomaX")
]
ServiceResponseType = Annotated[
    ServiceResponse, Field(description="Service response to OtomaX")
]
ErrorResponseType = Annotated[
    ErrorResponse, Field(description="Error response to OtomaX")
]
