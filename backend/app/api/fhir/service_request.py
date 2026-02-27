"""FHIR ServiceRequest resource endpoints.

Maps BloodTrace TransfusionRequest to FHIR ServiceRequest resource.
See: https://www.hl7.org/fhir/servicerequest.html
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rbac import require_roles
from app.models.user_models import User, UserRole
from app.services.transfusion_service import get_transfusion_request
from app.schemas.fhir_schemas import (
    FHIRServiceRequest,
    FHIRIdentifier,
    FHIRCodeableConcept,
    FHIRCoding,
    FHIRReference,
    FHIRMeta,
)

router = APIRouter()

# Map internal status to FHIR ServiceRequest status
STATUS_MAP = {
    "pending": "draft",
    "approved": "active",
    "in_progress": "active",
    "completed": "completed",
    "cancelled": "revoked",
}

# Map urgency to FHIR priority
PRIORITY_MAP = {
    "routine": "routine",
    "urgent": "urgent",
    "emergency": "stat",
    "massive": "stat",
}


def _request_to_fhir_service_request(request) -> FHIRServiceRequest:
    """Map a TransfusionRequest model to a FHIR ServiceRequest resource."""
    return FHIRServiceRequest(
        id=str(request.id),
        meta=FHIRMeta(
            lastUpdated=request.updated_at.isoformat() if request.updated_at else None,
        ),
        identifier=[
            FHIRIdentifier(
                system="http://bloodtrace.local/fhir/identifier/transfusion-request",
                value=str(request.id),
            ),
        ],
        status=STATUS_MAP.get(request.status, "unknown"),
        intent="order",
        priority=PRIORITY_MAP.get(request.urgency, "routine"),
        code=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://snomed.info/sct",
                    code="116859006",
                    display="Transfusion of blood product",
                ),
                FHIRCoding(
                    system="http://bloodtrace.local/fhir/blood-group",
                    code=f"{request.blood_type_needed}{request.rh_needed}",
                    display=f"Blood group {request.blood_type_needed}{request.rh_needed}",
                ),
            ],
            text=f"Transfusion {request.component_needed} - {request.blood_type_needed}{request.rh_needed}",
        ),
        subject=FHIRReference(
            reference=f"Patient/{request.patient_ipp}",
            display=request.patient_name,
        ),
        requester=FHIRReference(
            reference=f"Practitioner/{request.requesting_doctor_id}",
            display=request.requesting_doctor.name if request.requesting_doctor else None,
        ),
        reasonCode=[
            FHIRCodeableConcept(
                coding=[],
                text=request.clinical_indication,
            ),
        ],
        quantityQuantity={
            "value": request.units_needed,
            "unit": "units",
            "system": "http://unitsofmeasure.org",
            "code": "{units}",
        },
        authoredOn=request.created_at.isoformat() if request.created_at else None,
    )


@router.get("/ServiceRequest/{request_id}", response_model=FHIRServiceRequest)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def get_fhir_service_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a FHIR ServiceRequest resource by transfusion request ID.

    Returns standard FHIR R4 ServiceRequest JSON.
    """
    try:
        request = await get_transfusion_request(db, request_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail={
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-found",
                        "diagnostics": f"ServiceRequest with id '{request_id}' not found",
                    }
                ],
            },
        )

    return _request_to_fhir_service_request(request)


@router.post("/ServiceRequest", response_model=FHIRServiceRequest, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN])
async def create_fhir_service_request(
    fhir_request: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a transfusion request from a FHIR ServiceRequest.

    Accepts a standard FHIR R4 ServiceRequest JSON and maps it to an internal
    TransfusionRequest.
    """
    from app.schemas.transfusion_schemas import TransfusionRequestCreate
    from app.services.transfusion_service import create_transfusion_request

    try:
        # Extract data from FHIR resource
        subject_ref = fhir_request.get("subject", {}).get("reference", "")
        patient_ipp = subject_ref.replace("Patient/", "") if subject_ref else ""
        patient_name = fhir_request.get("subject", {}).get("display", "")

        # Extract blood type from code
        blood_code = ""
        for coding in fhir_request.get("code", {}).get("coding", []):
            if coding.get("system") == "http://bloodtrace.local/fhir/blood-group":
                blood_code = coding.get("code", "")
                break

        # Parse blood type and Rh from code
        if blood_code:
            rh = blood_code[-1]
            bt = blood_code[:-1]
        else:
            bt = "O"
            rh = "+"

        # Extract component from code text
        code_text = fhir_request.get("code", {}).get("text", "")
        component = "packed_rbc"
        for comp in ["whole_blood", "packed_rbc", "plasma", "platelets", "cryoprecipitate"]:
            if comp in code_text.lower():
                component = comp
                break

        # Extract units
        units = int(fhir_request.get("quantityQuantity", {}).get("value", 1))

        # Extract priority/urgency
        priority = fhir_request.get("priority", "routine")
        urgency_map = {"routine": "routine", "urgent": "urgent", "stat": "emergency"}
        urgency = urgency_map.get(priority, "routine")

        # Extract indication
        reason_codes = fhir_request.get("reasonCode", [])
        indication = reason_codes[0].get("text", "") if reason_codes else "FHIR ServiceRequest"

        request_data = TransfusionRequestCreate(
            patient_ipp=patient_ipp,
            patient_name=patient_name,
            blood_type_needed=bt,
            rh_needed=rh,
            component_needed=component,
            units_needed=units,
            urgency=urgency,
            clinical_indication=indication,
        )

        request = await create_transfusion_request(db, request_data, current_user.id)
        return _request_to_fhir_service_request(request)

    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "processing",
                        "diagnostics": str(e),
                    }
                ],
            },
        )
