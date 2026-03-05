"""FHIR Patient resource endpoints.

Maps BloodTrace Donor to FHIR Patient resource.
See: https://www.hl7.org/fhir/patient.html
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.rbac import require_roles
from app.models.user_models import User, UserRole
from app.services.donor_service import get_donor, get_donor_by_ipp
from app.schemas.fhir_schemas import (
    FHIRPatient,
    FHIRIdentifier,
    FHIRHumanName,
    FHIRMeta,
)

router = APIRouter()


def _donor_to_fhir_patient(donor) -> FHIRPatient:
    """Map a Donor model to a FHIR Patient resource."""
    telecom = []
    if donor.phone:
        telecom.append({"system": "phone", "value": donor.phone, "use": "home"})
    if donor.email:
        telecom.append({"system": "email", "value": donor.email, "use": "home"})

    # Blood type as extension
    extensions = [
        {
            "url": "http://bloodtrace.local/fhir/StructureDefinition/blood-type",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "882-1",
                        "display": f"ABO group: {donor.blood_type}",
                    }
                ],
                "text": f"{donor.blood_type}{donor.rh_factor}",
            },
        },
        {
            "url": "http://bloodtrace.local/fhir/StructureDefinition/rh-factor",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "10331-7",
                        "display": f"Rh: {donor.rh_factor}",
                    }
                ],
                "text": donor.rh_factor,
            },
        },
    ]

    return FHIRPatient(
        id=str(donor.id),
        meta=FHIRMeta(
            lastUpdated=donor.updated_at.isoformat() if donor.updated_at else None,
        ),
        identifier=[
            FHIRIdentifier(
                system="http://bloodtrace.local/fhir/identifier/ipp",
                value=donor.ipp,
            ),
        ],
        name=[
            FHIRHumanName(
                family=donor.last_name,
                given=[donor.first_name],
                text=f"{donor.first_name} {donor.last_name}",
            ),
        ],
        birthDate=donor.date_of_birth.isoformat() if donor.date_of_birth else None,
        telecom=telecom if telecom else None,
        extension=extensions,
    )


@router.get("/Patient/{patient_id}", response_model=FHIRPatient)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO])
async def get_fhir_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a FHIR Patient resource by donor ID or IPP.

    Returns standard FHIR R4 Patient JSON.
    """
    # Try by ID first, then by IPP
    donor = None
    if patient_id.isdigit():
        try:
            donor = await get_donor(db, int(patient_id))
        except Exception:
            pass

    if donor is None:
        donor = await get_donor_by_ipp(db, patient_id)

    if donor is None:
        raise HTTPException(
            status_code=404,
            detail={
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-found",
                        "diagnostics": f"Patient with identifier '{patient_id}' not found",
                    }
                ],
            },
        )

    return _donor_to_fhir_patient(donor)
