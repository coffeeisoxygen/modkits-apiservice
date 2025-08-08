"""Member service dependencies."""

from typing import Annotated

from app.dependencies.dep_repos import MemberRepDep
from app.dependencies.dep_signature import SignatureServiceDep
from app.schemas.sch_member import MemberInDB
from fastapi import Depends, HTTPException, status


class MemberService:
    """Service untuk handle member operations dan validasi."""

    def __init__(
        self,
        member_repo: MemberRepDep,
        signature_service: SignatureServiceDep,
    ):
        """Initialize member service.

        Args:
            member_repo: Member repository dependency
            signature_service: Signature service dependency
        """
        self.member_repo = member_repo
        self.signature_service = signature_service

    def get_member_by_id(self, member_id: str) -> MemberInDB:
        """Get member by ID dengan validation.

        Args:
            member_id: Member ID to find

        Returns:
            MemberInDB: Member data

        Raises:
            HTTPException: If member not found or inactive
        """
        member = self.member_repo.get_member_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with ID '{member_id}' not found",
            )

        if not member.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Member '{member_id}' is not active",
            )

        return member

    def validate_member_credentials(
        self,
        member_id: str,
        pin: str,
        password: str,
    ) -> MemberInDB:
        """Validate member credentials.

        Args:
            member_id: Member ID
            pin: Member PIN
            password: Member password

        Returns:
            MemberInDB: Validated member data

        Raises:
            HTTPException: If credentials invalid
        """
        member = self.get_member_by_id(member_id)

        # Validate PIN
        if member.pin.get_secret_value() != pin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN",
            )

        # Validate password
        if member.password.get_secret_value() != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password",
            )

        return member

    def validate_signature_if_required(
        self,
        member: MemberInDB,
        memberid: str,
        product: str,
        dest: str,
        refid: str,
        pin: str,
        password: str,
        sign: str | None = None,
    ) -> bool:
        """Validate signature if member requires it.

        Args:
            member: Member data
            memberid: Member ID for signature
            product: Product code for signature
            dest: Destination for signature
            refid: Reference ID for signature
            pin: PIN for signature
            password: Password for signature
            sign: Provided signature (optional)

        Returns:
            bool: True if validation passed

        Raises:
            HTTPException: If signature required but invalid/missing
        """
        # If member allows no signature, skip validation
        if member.allow_nosign:
            return True

        # If member requires signature but none provided
        if not sign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature required for this member",
            )

        # Generate expected signature
        expected_signature = self.signature_service.generate_transaction_signature(
            memberid=memberid,
            product=product,
            dest=dest,
            refid=refid,
            pin=pin,
            password=password,
        )

        # Compare signatures
        if sign != expected_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature",
            )

        return True


def get_member_service(
    member_repo: MemberRepDep,
    signature_service: SignatureServiceDep,
) -> MemberService:
    """Get member service instance.

    Args:
        member_repo: Member repository dependency
        signature_service: Signature service dependency

    Returns:
        MemberService: Configured member service
    """
    return MemberService(
        member_repo=member_repo,
        signature_service=signature_service,
    )


# Type alias for dependency injection
MemberServiceDep = Annotated[MemberService, Depends(get_member_service)]
