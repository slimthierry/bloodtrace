"""Tests for blood bag inventory endpoints."""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donor_models import Donor
from app.models.donation_models import Donation
from app.models.blood_bag_models import BloodBag
from tests.conftest import auth_headers
from datetime import datetime, timezone


async def _create_test_blood_bag(
    db_session: AsyncSession,
    admin_user,
    blood_type: str = "O",
    rh_factor: str = "-",
    component: str = "packed_rbc",
    status: str = "available",
    days_until_expiry: int = 30,
) -> BloodBag:
    """Helper to create a test blood bag with all required relations."""
    donor = Donor(
        ipp=f"IPP-{blood_type}{rh_factor}-{id(db_session)}",
        first_name="Test",
        last_name="Donor",
        date_of_birth=date(1990, 1, 1),
        blood_type=blood_type,
        rh_factor=rh_factor,
    )
    db_session.add(donor)
    await db_session.flush()

    donation = Donation(
        donor_id=donor.id,
        date=datetime.now(timezone.utc),
        volume_ml=450,
        collection_site="Centre EFS Test",
        collector_id=admin_user.id,
    )
    db_session.add(donation)
    await db_session.flush()

    bag = BloodBag(
        donation_id=donation.id,
        blood_type=blood_type,
        rh_factor=rh_factor,
        component=component,
        volume_ml=450,
        collection_date=date.today(),
        expiry_date=date.today() + timedelta(days=days_until_expiry),
        status=status,
        storage_location="Fridge A",
        storage_temperature=4.0,
    )
    db_session.add(bag)
    await db_session.commit()
    await db_session.refresh(bag)
    return bag


@pytest.mark.asyncio
async def test_get_stock_summary(
    client: AsyncClient, db_session: AsyncSession, admin_user, admin_token
):
    """Test stock summary returns all 8 blood groups."""
    response = await client.get(
        "/api/v1/inventory/stock",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["levels"]) == 8
    blood_groups = {level["blood_group"] for level in data["levels"]}
    assert blood_groups == {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


@pytest.mark.asyncio
async def test_create_and_list_blood_bags(
    client: AsyncClient, db_session: AsyncSession, admin_user, admin_token
):
    """Test listing blood bags."""
    await _create_test_blood_bag(db_session, admin_user, "A", "+")

    response = await client.get(
        "/api/v1/inventory",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_filter_blood_bags_by_type(
    client: AsyncClient, db_session: AsyncSession, admin_user, admin_token
):
    """Test filtering blood bags by blood type."""
    await _create_test_blood_bag(db_session, admin_user, "B", "+")

    response = await client.get(
        "/api/v1/inventory?blood_type=B&rh_factor=%2B",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    for bag in data["blood_bags"]:
        assert bag["blood_type"] == "B"


@pytest.mark.asyncio
async def test_compatibility_matrix(
    client: AsyncClient, admin_user, admin_token
):
    """Test getting the full compatibility matrix."""
    response = await client.get(
        "/api/v1/inventory/compatibility",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "rbc" in data
    assert "plasma" in data
    assert "blood_groups" in data
    assert len(data["blood_groups"]) == 8


@pytest.mark.asyncio
async def test_check_compatibility(
    client: AsyncClient, admin_user, admin_token
):
    """Test checking specific blood compatibility."""
    # O- can donate to anyone (universal donor for RBC)
    response = await client.get(
        "/api/v1/inventory/compatibility/check"
        "?donor_type=O&donor_rh=-&recipient_type=AB&recipient_rh=%2B",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["compatible"] is True
