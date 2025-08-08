from app.dependencies.dep_signature import SignatureServiceDep
from fastapi import APIRouter

router = APIRouter(prefix="/service", tags=["service"])


@router.get("/service")
async def get_service(signature: SignatureServiceDep):
    return {"message": "Service is running", "signature": signature}
