"""Tests for blood donor endpoints."""

import pytest
from datetime import date

from app.models.donor_models import Donor, BloodType, RhFactor, EligibilityStatus
from app.models.user_models import User, UserRole
from app.auth.security import get_password_hash

from tests.conftest import auth_headers


async def create_donor(db_session, **overrides):
    """Helper to create a donor in the test database."""
    donor = Donor(
        ipp=overrides.get("ipp", "IPP001"),
        first_name=overrides.get("first_name", "Thierry"),
        last_name=overrides.get("last_name", "Sessou"),
        date_of_birth=overrides.get("date_of_birth", date(1990, 1, 15)),
        blood_type=BloodType.A.value,
        rh_factor=RhFactor.POSITIVE.value,
        eligibility_status=EligibilityStatus.ELIGIBLE.value,
        phone=overrides.get("phone", "+22890000001"),
        email=overrides.get("email", "thierry@test.com"),
        donation_count=0,
    )
    db_session.add(donor)
    await db_session.commit()
    await db_session.refresh(donor)
    return donor


# ========================
# Create Donor
# ========================

@pytest.mark.asyncio
async def test_create_donor_success(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test admin can create a new donor."""
    payload = {
        "ipp": "IPP_NEW_001",
        "first_name": "Koffi",
        "last_name": "Ama",
        "date_of_birth": "1985-06-20",
        "blood_type": "O",
        "rh_factor": "+",
        "phone": "+22890112233",
        "email": "koffi@ama.test",
    }
    response = await client.post(
        "/api/v1/donors",
        json=payload,
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ipp"] == "IPP_NEW_001"
    assert data["first_name"] == "Koffi"
    assert data["blood_type"] == "A"  # normalized
    assert data["rh_factor"] == "+"
    assert data["eligibility_status"] == "eligible"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_donor_duplicate_ipp(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test creating a donor with existing IPP returns 409."""
    await create_donor(db_session, ipp="IPP_DUP")
    response = await client.post(
        "/api/v1/donors",
        json={
            "ipp": "IPP_DUP",
            "first_name": "Dup",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "blood_type": "A",
            "rh_factor": "+",
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_donor_medecin_forbidden(client: AsyncClient, medecin_user, medecin_token, db_session: AsyncSession):
    """Test medecin cannot create donors (not their role)."""
    response = await client.post(
        "/api/v1/donors",
        json={
            "ipp": "IPP_MED_001",
            "first_name": "Med",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "blood_type": "B",
            "rh_factor": "-",
        },
        headers=auth_headers(medecin_token),
    )
    assert response.status_code == 403


# ========================
# List Donors
# ========================

@pytest.mark.asyncio
async def test_list_donors_empty(client: AsyncClient, admin_user, admin_token):
    """Test listing donors when none exist."""
    response = await client.get(
        "/api/v1/donors",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["donors"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_donors_with_data(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test listing donors returns created donors."""
    await create_donor(db_session, ipp="IPP_LST_001")
    await create_donor(db_session, ipp="IPP_LST_002", first_name="Koami")

    response = await client.get(
        "/api/v1/donors",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["donors"]) >= 2


@pytest.mark.asyncio
async def test_list_donors_pagination(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test donor list pagination."""
    for i in range(5):
        await create_donor(db_session, ipp=f"IPP_PAG_{i}")

    response = await client.get(
        "/api/v1/donors?skip=0&limit=2",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["donors"]) == 2
    assert data["total"] >= 5


@pytest.mark.asyncio
async def test_list_donors_search(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test searching donors by name."""
    await create_donor(db_session, ipp="IPP_SCH_001", first_name="Sébastien", last_name="Koffi")
    await create_donor(db_session, ipp="IPP_SCH_002", first_name="Marcel", last_name="Ama")

    response = await client.get(
        "/api/v1/donors?search=seb",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert any(d["first_name"] == "Sébastien" for d in data["donors"])


@pytest.mark.asyncio
async def test_list_donors_by_blood_type(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test filtering donors by blood type."""
    await create_donor(db_session, ipp="IPP_BT_001", blood_type=BloodType.O.value)
    await create_donor(db_session, ipp="IPP_BT_002", blood_type=BloodType.AB.value)

    response = await client.get(
        "/api/v1/donors?blood_type=O",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    for d in data["donors"]:
        assert d["blood_type"] == "O"


@pytest.mark.asyncio
async def test_list_donors_unauthorized(client: AsyncClient):
    """Test listing donors without auth fails."""
    response = await client.get("/api/v1/donors")
    assert response.status_code == 401


# ========================
# Get Donor
# ========================

@pytest.mark.asyncio
async def test_get_donor_by_id(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test getting a single donor by ID."""
    donor = await create_donor(db_session, ipp="IPP_GET_001")

    response = await client.get(
        f"/api/v1/donors/{donor.id}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == donor.id
    assert data["ipp"] == "IPP_GET_001"


@pytest.mark.asyncio
async def test_get_donor_not_found(client: AsyncClient, admin_user, admin_token):
    """Test getting a non-existent donor returns 404."""
    response = await client.get(
        "/api/v1/donors/99999",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 404


# ========================
# Update Donor
# ========================

@pytest.mark.asyncio
async def test_update_donor_success(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test updating a donor's eligibility status."""
    donor = await create_donor(db_session, ipp="IPP_UPD_001")

    response = await client.patch(
        f"/api/v1/donors/{donor.id}",
        json={"eligibility_status": "temporary_deferral", "deferral_reason": "Anémie"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligibility_status"] == "temporary_deferral"
    assert data["deferral_reason"] == "Anémie"


@pytest.mark.asyncio
async def test_update_donor_nonexistent(client: AsyncClient, admin_user, admin_token):
    """Test updating non-existent donor returns 404."""
    response = await client.patch(
        "/api/v1/donors/99999",
        json={"phone": "+22899999999"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 404


# ========================
# Deferral
# ========================

@pytest.mark.asyncio
async def test_defer_donor(client: AsyncClient, admin_user, admin_token, db_session: AsyncSession):
    """Test temporarily deferring a donor."""
    donor = await create_donor(db_session, ipp="IPP_DEF_001")

    response = await client.post(
        f"/api/v1/donors/{donor.id}/defer",
        json={"reason": " Grippe", "duration_days": 14},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligibility_status"] == "temporary_deferral"
    assert data["deferral_reason"] == "Grippe"