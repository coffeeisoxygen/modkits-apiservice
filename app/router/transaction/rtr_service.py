"""Service endpoint for handling OtomaX transactions."""

from app.dependencies.dep_member import MemberServiceDep
from app.dependencies.dep_signature import SignatureServiceDep
from app.schemas.sch_service import (
    ErrorResponse,
    ServiceRequest,
    ServiceResponse,
    SignatureValidationRequest,
)
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/service", tags=["Service"])


@router.post("/transaction", response_model=ServiceResponse)
async def process_transaction(
    request: ServiceRequest,
    member_service: MemberServiceDep,
) -> ServiceResponse | JSONResponse:
    """Process transaction request from OtomaX.

    Flow:
    1. Validate member credentials
    2. Check signature (if required)
    3. Process transaction
    4. Return response
    """
    try:
        # Get member to validate it exists and is active
        _member = member_service.get_member_by_id(request.memberid)

        # For demonstration, assume we have member credentials available
        # In real implementation, these might come from different source
        # member_service.validate_member_credentials(
        #     member_id=request.memberid,
        #     pin="dummy_pin",  # This needs to come from request
        #     password="dummy_password"  # This needs to come from request
        # )

        # Validate signature if required
        # member_service.validate_signature_if_required(
        #     member=member,
        #     memberid=request.memberid,
        #     product=request.product,
        #     dest=request.dest,
        #     refid=request.refid,
        #     pin="dummy_pin",
        #     password="dummy_password",
        #     sign=request.sign,
        # )

        # Process transaction (core business logic will go here)
        # For now, return success response

        return ServiceResponse(
            status="success",
            message="Transaction processed successfully",
            refid=request.refid,
            data={
                "product": request.product,
                "dest": request.dest,
                "qty": request.qty,
                "member": request.memberid,
                "sn": "1234567890",  # Dummy serial number
                "balance": 95000,  # Dummy remaining balance
            },
        )

    except HTTPException as e:
        # Convert HTTPException to ErrorResponse
        error_response = ErrorResponse(
            message=e.detail, refid=request.refid, error_code=str(e.status_code)
        )
        return JSONResponse(
            status_code=e.status_code, content=error_response.model_dump()
        )
    except Exception:
        # Handle unexpected errors
        error_response = ErrorResponse(
            message="Internal server error",
            refid=request.refid,
            error_code="INTERNAL_ERROR",
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
    """Validate signature for testing purposes."""
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


@router.get("/health")
async def service_health() -> dict:
    """Health check for service endpoint."""
    return {
        "status": "healthy",
        "service": "transaction-service",
        "endpoints": [
            "/service/transaction",
            "/service/validate-signature",
            "/service/health",
        ],
    }
