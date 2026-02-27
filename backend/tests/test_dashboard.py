"""Tests for dashboard endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_dashboard_returns_all_sections(
    client: AsyncClient, admin_user, admin_token
):
    """Test dashboard returns all required data sections."""
    response = await client.get(
        "/api/v1/dashboard",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()

    # Verify all dashboard sections are present
    assert "stock_levels" in data
    assert "total_available" in data
    assert "expiring_alerts" in data
    assert "pending_requests" in data
    assert "recent_transfusions" in data
    assert "stats" in data


@pytest.mark.asyncio
async def test_dashboard_stock_levels_all_groups(
    client: AsyncClient, admin_user, admin_token
):
    """Test dashboard stock levels include all 8 blood groups."""
    response = await client.get(
        "/api/v1/dashboard",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["stock_levels"]) == 8
    groups = {level["blood_group"] for level in data["stock_levels"]}
    expected = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    assert groups == expected


@pytest.mark.asyncio
async def test_dashboard_stats_structure(
    client: AsyncClient, admin_user, admin_token
):
    """Test dashboard stats contain all expected fields."""
    response = await client.get(
        "/api/v1/dashboard",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    stats = response.json()["stats"]

    assert "total_donors" in stats
    assert "total_donations_this_month" in stats
    assert "total_transfusions_this_month" in stats
    assert "total_blood_bags_available" in stats
    assert "total_pending_requests" in stats
    assert "reactions_this_month" in stats


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    """Test dashboard requires authentication."""
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint is accessible without auth."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "bloodtrace"
