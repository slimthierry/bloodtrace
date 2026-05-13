"""Tests for transfusion endpoints."""

import pytest
from datetime import date

from app.models.donor_models import Donor, BloodType, RhFactor, EligibilityStatus
from app.models.blood_bag_models import BloodBag, BloodBagStatus
from app.models.transfusion_models import (
    TransfusionRequest,
    Transfusion,
    Urgency,
    RequestStatus,
    ReactionType,
)
from app.models.user_models import User, UserRole

from tests.conftest import auth_headers


async def create_donor(db_session, **overrides):
    donor = Donor(
        ipp=overrides.get("ipp", "IPP_TRX_DNR"),
        first_name=overrides.get("first_name", "Donor"),
        last_name=overrides.get("last_name", "Test"),
        date_of_birth=overrides.get("date_of_birth", date(1985, 5, 10)),
        blood_type=overrides.get("blood_type", BloodType.A.value),
        rh_factor=overrides.get("rh_factor", RhFactor.POSITIVE.value),
        eligibility_status=EligibilityStatus.ELIGIBLE.value,
        phone="+22890000000",
        email="donor@test.com",
        donation_count=1,
    )
    db_session.add(donor)
    await db_session.commit()
    await db_session.refresh(donor)
    return donor


async def create_blood_bag(db_session, donor: Donor, **overrides):
    bag = BloodBag(
        bag_number=overrides.get("bag_number", "BK_TRX_001"),
        donor_id=donor.id,
        blood_type=donor.blood_type,
        rh_factor=donor.rh_factor,
        component=overrides.get("component", "PFC"),
        volume_ml=overrides.get("volume_ml", 250),
        collection_date=date.today(),
        expiry_date=overrides.get("expiry_date", date(2030, 1, 1)),
        status=overrides.get("status", BloodBagStatus.AVAILABLE.value),
    )
    db_session.add(bag)
    await db_session.commit()
    await db_session.refresh(bag)
    return bag


# ========================
# Transfusion Requests
# ========================

@pytest.mark.asyncio
async def test_create_transfusion_request(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test creating a transfusion request."""
    response = await client.post(
        "/api/v1/transfusions/requests",
        json={
            "patient_ipp": "IPP_PTR_001",
            "patient_name": "Patient Test",
            "blood_type_needed": "A",
            "rh_needed": "+",
            "component_needed": "PFC",
            "units_needed": 2,
            "urgency": "urgent",
            "clinical_indication": "Chirurgie programmée",
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["patient_ipp"] == "IPP_PTR_001"
    assert data["urgency"] == "urgent"
    assert data["status"] == "pending"
    assert data["units_needed"] == 2


@pytest.mark.asyncio
async def test_list_transfusion_requests(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test listing transfusion requests."""
    # Create a request first
    req = TransfusionRequest(
        patient_ipp="IPP_LTR_001",
        patient_name="LTR Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="O",
        rh_needed="+",
        component_needed="CGR",
        units_needed=3,
        urgency=Urgency.ROUTINE.value,
        clinical_indication="Anémie sévère",
        status=RequestStatus.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()

    response = await client.get(
        "/api/v1/transfusions/requests",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(r["patient_ipp"] == "IPP_LTR_001" for r in data["requests"])


@pytest.mark.asyncio
async def test_list_transfusion_requests_by_status(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test filtering requests by status."""
    req = TransfusionRequest(
        patient_ipp="IPP_STS_001",
        patient_name="Status Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="B",
        rh_needed="-",
        component_needed="PFC",
        units_needed=1,
        urgency=Urgency.EMERGENCY.value,
        clinical_indication="Hémorragie",
        status=RequestStatus.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()

    response = await client.get(
        "/api/v1/transfusions/requests?status=pending",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    for r in data["requests"]:
        assert r["status"] == "pending"


@pytest.mark.asyncio
async def test_get_transfusion_request(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test getting a single transfusion request."""
    req = TransfusionRequest(
        patient_ipp="IPP_GTR_001",
        patient_name="Get Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="AB",
        rh_needed="+",
        component_needed="CGR",
        units_needed=1,
        urgency=Urgency.ROUTINE.value,
        clinical_indication="Test",
        status=RequestStatus.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    response = await client.get(
        f"/api/v1/transfusions/requests/{req.id}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == req.id
    assert data["patient_ipp"] == "IPP_GTR_001"


@pytest.mark.asyncio
async def test_approve_transfusion_request(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test approving a transfusion request."""
    req = TransfusionRequest(
        patient_ipp="IPP_APR_001",
        patient_name="Approve Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="O",
        rh_needed="-",
        component_needed="PFC",
        units_needed=2,
        urgency=Urgency.URGENT.value,
        clinical_indication="Chirurgie",
        status=RequestStatus.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    response = await client.post(
        f"/api/v1/transfusions/requests/{req.id}/approve",
        json={"approved_by_id": admin_user.id, "notes": "Approuvé pour chirurgie"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_cancel_transfusion_request(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test cancelling a transfusion request."""
    req = TransfusionRequest(
        patient_ipp="IPP_CAN_001",
        patient_name="Cancel Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="A",
        rh_needed="+",
        component_needed="CGR",
        units_needed=1,
        urgency=Urgency.ROUTINE.value,
        clinical_indication="Test",
        status=RequestStatus.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    response = await client.post(
        f"/api/v1/transfusions/requests/{req.id}/cancel",
        json={"reason": "Patient non disponible"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


# ========================
# Traceability
# ========================

@pytest.mark.asyncio
async def test_get_traceability_chain(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test full traceability chain from donor to transfusion."""
    donor = await create_donor(db_session, ipp="IPP_TRC_DNR", first_name="Trace", last_name="Donor")
    bag = await create_blood_bag(db_session, donor, bag_number="BK_TRC_001")

    req = TransfusionRequest(
        patient_ipp="IPP_TRC_PTR",
        patient_name="Trace Patient",
        requesting_doctor_id=admin_user.id,
        blood_type_needed="A",
        rh_needed="+",
        component_needed="PFC",
        units_needed=1,
        urgency=Urgency.ROUTINE.value,
        clinical_indication="Trace test",
        status=RequestStatus.COMPLETED.value,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    transfusion = Transfusion(
        request_id=req.id,
        blood_bag_id=bag.id,
        patient_ipp="IPP_TRC_PTR",
        units_transfused=1,
        volume_transfused_ml=250,
        start_time=None,
        end_time=None,
        reaction_type=ReactionType.NONE.value,
        performed_by_id=admin_user.id,
    )
    db_session.add(transfusion)
    await db_session.commit()
    await db_session.refresh(transfusion)

    response = await client.get(
        f"/api/v1/transfusions/{req.id}/trace",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "request" in data
    assert "transfusions" in data


# ========================
# Compatibility Matrix
# ========================

@pytest.mark.asyncio
async def test_compatibility_matrix(
    client: AsyncClient, admin_user, admin_token, db_session: AsyncSession
):
    """Test retrieving blood compatibility matrix."""
    response = await client.get(
        "/api/v1/inventory/compatibility",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data
    # O- should be universal donor
    assert data["matrix"]["O-"]["can_receive_from"] == ["O-"]
    # AB+ should be universal recipient
    assert data["matrix"]["AB+"]["can_donate_to"] == ["AB+"]