"""FHIR Specimen resource endpoints.

Maps BloodTrace BloodBag to FHIR Specimen resource.
See: https://www.hl7.org/fhir/specimen.html
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rbac import require_roles
from app.models.user_models import User, UserRole
from app.services.inventory_service import get_blood_bag
from app.schemas.fhir_schemas import (
    FHIRSpecimen,
    FHIRIdentifier,
    FHIRCodeableConcept,
    FHIRCoding,
    FHIRReference,
    FHIRMeta,
)

router = APIRouter()

# Map component types to SNOMED CT codes
COMPONENT_SNOMED = {
    "whole_blood": ("119297000", "Blood specimen"),
    "packed_rbc": ("708048008", "Red blood cells unit"),
    "plasma": ("119361006", "Plasma specimen"),
    "platelets": ("119305000", "Platelet concentrate"),
    "cryoprecipitate": ("708047003", "Cryoprecipitate unit"),
}

# Map bag status to FHIR specimen status
STATUS_MAP = {
    "available": "available",
    "reserved": "available",
    "crossmatched": "available",
    "transfused": "unavailable",
    "expired": "unavailable",
    "discarded": "unavailable",
    "quarantine": "unavailable",
}


def _blood_bag_to_fhir_specimen(bag) -> FHIRSpecimen:
    """Map a BloodBag model to a FHIR Specimen resource."""
    snomed_code, snomed_display = COMPONENT_SNOMED.get(
        bag.component, ("119297000", "Blood specimen")
    )

    # Build container info
    container = {
        "description": f"Blood bag - {bag.component}",
        "capacity": {"value": bag.volume_ml, "unit": "mL"},
    }
    if bag.storage_location:
        container["description"] += f" at {bag.storage_location}"

    # Build collection info
    collection = {
        "collectedDateTime": bag.collection_date.isoformat(),
    }

    return FHIRSpecimen(
        id=str(bag.id),
        meta=FHIRMeta(
            lastUpdated=bag.updated_at.isoformat() if bag.updated_at else None,
        ),
        identifier=[
            FHIRIdentifier(
                system="http://bloodtrace.local/fhir/identifier/blood-bag",
                value=str(bag.id),
            ),
        ],
        type=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://snomed.info/sct",
                    code=snomed_code,
                    display=snomed_display,
                ),
                FHIRCoding(
                    system="http://bloodtrace.local/fhir/blood-group",
                    code=f"{bag.blood_type}{bag.rh_factor}",
                    display=f"Blood group {bag.blood_type}{bag.rh_factor}",
                ),
            ],
            text=f"{bag.blood_type}{bag.rh_factor} - {bag.component}",
        ),
        subject=FHIRReference(
            reference=f"Patient/{bag.donation.donor_id}" if bag.donation else None,
        ) if bag.donation else None,
        collection=collection,
        container=[container],
        status=STATUS_MAP.get(bag.status, "unavailable"),
    )


@router.get("/Specimen/{specimen_id}", response_model=FHIRSpecimen)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def get_fhir_specimen(
    specimen_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a FHIR Specimen resource by blood bag ID.

    Returns standard FHIR R4 Specimen JSON.
    """
    try:
        bag = await get_blood_bag(db, specimen_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail={
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-found",
                        "diagnostics": f"Specimen with id '{specimen_id}' not found",
                    }
                ],
            },
        )

    return _blood_bag_to_fhir_specimen(bag)
