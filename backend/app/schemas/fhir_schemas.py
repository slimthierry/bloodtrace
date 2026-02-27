"""FHIR-compatible schemas for SIH integration.

Follows HL7 FHIR R4 resource structure for:
- Patient (mapped from Donor)
- Specimen (mapped from BloodBag)
- ServiceRequest (mapped from TransfusionRequest)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --- FHIR Common Types ---

class FHIRCoding(BaseModel):
    """FHIR Coding type."""

    system: str
    code: str
    display: Optional[str] = None


class FHIRCodeableConcept(BaseModel):
    """FHIR CodeableConcept type."""

    coding: list[FHIRCoding]
    text: Optional[str] = None


class FHIRIdentifier(BaseModel):
    """FHIR Identifier type."""

    system: str
    value: str


class FHIRReference(BaseModel):
    """FHIR Reference type."""

    reference: str
    display: Optional[str] = None


class FHIRHumanName(BaseModel):
    """FHIR HumanName type."""

    family: str
    given: list[str]
    text: Optional[str] = None


class FHIRMeta(BaseModel):
    """FHIR Meta type."""

    versionId: Optional[str] = None
    lastUpdated: Optional[str] = None


# --- FHIR Resources ---

class FHIRPatient(BaseModel):
    """FHIR Patient resource (mapped from Donor).

    See: https://www.hl7.org/fhir/patient.html
    """

    resourceType: str = "Patient"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: list[FHIRIdentifier]
    name: list[FHIRHumanName]
    birthDate: Optional[str] = None
    telecom: Optional[list[dict]] = None
    extension: Optional[list[dict]] = None


class FHIRSpecimen(BaseModel):
    """FHIR Specimen resource (mapped from BloodBag).

    See: https://www.hl7.org/fhir/specimen.html
    """

    resourceType: str = "Specimen"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: list[FHIRIdentifier]
    type: FHIRCodeableConcept
    subject: Optional[FHIRReference] = None
    collection: Optional[dict] = None
    processing: Optional[list[dict]] = None
    container: Optional[list[dict]] = None
    status: Optional[str] = None


class FHIRServiceRequest(BaseModel):
    """FHIR ServiceRequest resource (mapped from TransfusionRequest).

    See: https://www.hl7.org/fhir/servicerequest.html
    """

    resourceType: str = "ServiceRequest"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: list[FHIRIdentifier]
    status: str
    intent: str = "order"
    priority: Optional[str] = None
    code: FHIRCodeableConcept
    subject: FHIRReference
    requester: Optional[FHIRReference] = None
    reasonCode: Optional[list[FHIRCodeableConcept]] = None
    quantityQuantity: Optional[dict] = None
    authoredOn: Optional[str] = None


class FHIRBundle(BaseModel):
    """FHIR Bundle resource for search results."""

    resourceType: str = "Bundle"
    type: str = "searchset"
    total: int
    entry: list[dict]
