"""Service endpoint for handling OtomaX transactions via GET method."""

from app.dependencies.dep_member import MemberServiceDep
from app.dependencies.dep_signature import SignatureServiceDep
from app.schemas.sch_service import (
    ErrorResponse,
    ServiceResponse,
    SignatureValidationRequest,
)
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/service", tags=["Service"])


@router.get("/transaction")
async def process_transaction(
    product: str = Query(..., description="Product code"),
    qty: int = Query(1, description="Quantity", ge=1, le=1000),
    dest: str = Query(
        ..., description="Destination phone number", min_length=10, max_length=15
    ),
    refid: str = Query(..., description="Reference/Transaction ID"),
    memberid: str = Query(..., description="Member ID"),
    sign: str | None = Query(None, description="Signature for verification"),
    pin: str | None = Query(None, description="Member PIN (if no signature)"),
    password: str | None = Query(None, description="Member password (if no signature)"),
    member_service: MemberServiceDep = None,
) -> ServiceResponse | JSONResponse:
    """Process transaction request from OtomaX via GET.

    OtomaX Request Examples:
    1. With signature (allow_nosign=False or True):
       GET /service/transaction?product=CLPDATA&qty=1&dest=081295221639&refid=3040881&memberid=mem_001&pin=1234&password=member123&sign=MsP6Aticed6s1rlEhvj4NKceFVQ

    2. Without signature (allow_nosign=True only):
       GET /service/transaction?product=CLPDATA&qty=1&dest=081295221639&refid=3040881&memberid=mem_002&pin=5678&password=member456

    Member Logic:
    - allow_nosign=False: MUST have valid signature + pin + password
    - allow_nosign=True: Can use signature OR just pin + password
    """
    try:
        # 1. Get member and validate exists + active
        member = member_service.get_member_by_id(memberid)

        # 2. Validate authentication based on member's allow_nosign setting
        if member.allow_nosign:
            # Member allows no signature - accept either signature OR pin+password
            if sign:
                # Signature provided - validate it (need pin+password for validation)
                if not pin or not password:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="PIN and password required for signature validation",
                    )

                # Validate credentials first
                member_service.validate_member_credentials(
                    member_id=memberid,
                    pin=pin,
                    password=password,
                )

                # Then validate signature
                member_service.validate_signature_if_required(
                    member=member,
                    memberid=memberid,
                    product=product,
                    dest=dest,
                    refid=refid,
                    pin=pin,
                    password=password,
                    sign=sign,
                )
                auth_method = "signature"

            elif pin and password:
                # No signature but credentials provided - validate credentials only
                member_service.validate_member_credentials(
                    member_id=memberid,
                    pin=pin,
                    password=password,
                )
                auth_method = "credentials"

            else:
                # Neither signature nor credentials - not allowed
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either signature or PIN+password required",
                )
        else:
            # Member requires signature - MUST have signature with credentials
            if not sign:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Signature required for member '{memberid}' (allow_nosign=False)",
                )

            if not pin or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PIN and password required for signature validation",
                )

            # Validate credentials first
            member_service.validate_member_credentials(
                member_id=memberid,
                pin=pin,
                password=password,
            )

            # Then validate signature
            member_service.validate_signature_if_required(
                member=member,
                memberid=memberid,
                product=product,
                dest=dest,
                refid=refid,
                pin=pin,
                password=password,
                sign=sign,
            )
            auth_method = "signature"

        # 3. Process transaction (core business logic will go here)
        # TODO: Implement actual transaction processing logic
        # TODO: Call to module service based on product
        # TODO: Handle different product types

        return ServiceResponse(
            status="success",
            message="Transaction processed successfully",
            refid=refid,
            data={
                "product": product,
                "dest": dest,
                "qty": qty,
                "member": memberid,
                "sn": "1234567890",  # Dummy serial number - replace with actual
                "balance": 95000,  # Dummy remaining balance - replace with actual
                "auth_method": auth_method,
                "allow_nosign": member.allow_nosign,
                "member_ip": member.ip_address,
            },
        )

    except HTTPException as e:
        # Convert HTTPException to ErrorResponse
        error_response = ErrorResponse(
            message=e.detail, refid=refid, error_code=str(e.status_code)
        )
        return JSONResponse(
            status_code=e.status_code, content=error_response.model_dump()
        )
    except Exception:
        # Handle unexpected errors
        error_response = ErrorResponse(
            message="Internal server error", refid=refid, error_code="INTERNAL_ERROR"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )


@router.post("/validate-signature")
async def validate_signature(
    request: SignatureValidationRequest,
    signature_service: SignatureServiceDep,
) -> dict:
    """Validate signature for testing purposes (POST method)."""
    try:
        generated_signature = signature_service.generate_transaction_signature(
            memberid=request.memberid,
            product=request.product,
            dest=request.dest,
            refid=request.refid,
            pin=request.pin,
            password=request.password,
        )

        is_valid = request.sign == generated_signature

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature validation failed: {e!s}",
        ) from e
    else:
        return {
            "provided_signature": request.sign,
            "generated_signature": generated_signature,
            "is_valid": is_valid,
            "member": request.memberid,
            "refid": request.refid,
        }


@router.get("/validate-signature")
async def validate_signature_get(
    memberid: str = Query(..., description="Member ID"),
    product: str = Query(..., description="Product code"),
    dest: str = Query(..., description="Destination"),
    refid: str = Query(..., description="Reference ID"),
    pin: str = Query(..., description="Member PIN"),
    password: str = Query(..., description="Member password"),
    sign: str = Query(..., description="Signature to validate"),
    signature_service: SignatureServiceDep = None,
) -> dict:
    """Validate signature via GET for testing purposes."""
    try:
        generated_signature = signature_service.generate_transaction_signature(
            memberid=memberid,
            product=product,
            dest=dest,
            refid=refid,
            pin=pin,
            password=password,
        )

        is_valid = sign == generated_signature

        return {
            "provided_signature": sign,
            "generated_signature": generated_signature,
            "is_valid": is_valid,
            "member": memberid,
            "refid": refid,
            "raw_string": f"OtomaX|{memberid.upper()}|{product.upper()}|{dest}|{refid}|{pin}|{password}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature validation failed: {e!s}",
        ) from e


@router.get("/test-members")
async def test_members(
    member_service: MemberServiceDep = None,
) -> dict:
    """Test endpoint to show member configuration."""
    try:
        # Get all members from repository
        all_members = member_service.member_repo.get_all_members()

        members_info = []
        for member in all_members:
            members_info.append({
                "member_id": member.member_id,
                "is_active": member.is_active,
                "allow_nosign": member.allow_nosign,
                "ip_address": member.ip_address,
                "report_url": str(member.report_url),
            })

        return {
            "total_members": len(all_members),
            "members": members_info,
            "usage_examples": {
                "with_signature": "/service/transaction?product=CLPDATA&qty=1&dest=081295221639&refid=3040881&memberid=mem_001&pin=1234&password=member123&sign=SIGNATURE_HERE",
                "without_signature": "/service/transaction?product=CLPDATA&qty=1&dest=081295221639&refid=3040881&memberid=mem_002&pin=5678&password=member456",
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get members: {e!s}",
        ) from e


@router.get("/health")
async def service_health() -> dict:
    """Health check for service endpoint."""
    return {
        "status": "healthy",
        "service": "transaction-service",
        "request_method": "GET",
        "endpoints": [
            "GET /service/transaction - Main transaction processor",
            "POST /service/validate-signature - Signature validation (POST)",
            "GET /service/validate-signature - Signature validation (GET)",
            "GET /service/test-members - Show member configurations",
            "GET /service/health - Health check",
        ],
        "member_auth_logic": {
            "allow_nosign=True": "Accept signature OR pin+password",
            "allow_nosign=False": "MUST have signature + pin + password",
        },
    }
