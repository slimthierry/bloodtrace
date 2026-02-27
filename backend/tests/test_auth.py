"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    """Test successful login returns token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@bloodtrace.test", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"
    assert data["email"] == "admin@bloodtrace.test"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user):
    """Test login with wrong password fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@bloodtrace.test", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@bloodtrace.test", "password": "test123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, admin_user, admin_token):
    """Test retrieving current user info."""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@bloodtrace.test"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test accessing protected endpoint without token fails."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_user_as_admin(client: AsyncClient, admin_user, admin_token):
    """Test admin can register a new user."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@bloodtrace.test",
            "name": "New User",
            "password": "newuser123",
            "role": "technicien_labo",
            "service": "Laboratoire",
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@bloodtrace.test"
    assert data["role"] == "technicien_labo"
