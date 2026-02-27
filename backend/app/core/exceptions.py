"""Custom exception classes for BloodTrace."""

from fastapi import HTTPException, status


class BloodTraceException(HTTPException):
    """Base exception for BloodTrace."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class DonorNotFoundException(BloodTraceException):
    """Raised when a donor is not found."""

    def __init__(self, donor_id: int):
        super().__init__(
            detail=f"Donneur avec l'ID {donor_id} non trouve",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BloodBagNotFoundException(BloodTraceException):
    """Raised when a blood bag is not found."""

    def __init__(self, bag_id: int):
        super().__init__(
            detail=f"Poche de sang avec l'ID {bag_id} non trouvee",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class IncompatibleBloodException(BloodTraceException):
    """Raised when blood types are incompatible."""

    def __init__(self, donor_type: str, recipient_type: str):
        super().__init__(
            detail=f"Incompatibilite sanguine: donneur {donor_type} vers receveur {recipient_type}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class InsufficientStockException(BloodTraceException):
    """Raised when blood stock is insufficient."""

    def __init__(self, blood_type: str, component: str):
        super().__init__(
            detail=f"Stock insuffisant pour {blood_type} ({component})",
            status_code=status.HTTP_409_CONFLICT,
        )


class DonorIneligibleException(BloodTraceException):
    """Raised when a donor is not eligible for donation."""

    def __init__(self, reason: str):
        super().__init__(
            detail=f"Donneur non eligible: {reason}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class TransfusionRequestNotFoundException(BloodTraceException):
    """Raised when a transfusion request is not found."""

    def __init__(self, request_id: int):
        super().__init__(
            detail=f"Demande de transfusion avec l'ID {request_id} non trouvee",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedAccessException(BloodTraceException):
    """Raised when a user lacks required permissions."""

    def __init__(self, action: str):
        super().__init__(
            detail=f"Acces non autorise pour l'action: {action}",
            status_code=status.HTTP_403_FORBIDDEN,
        )
