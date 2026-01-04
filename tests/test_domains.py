"""Tests for domain endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_domain(client: AsyncClient):
    """Test creating a domain."""
    response = await client.post(
        "/api/v1/domains",
        json={
            "name": "VR Chat",
            "slug": "vr-chat",
            "description": "Chat domain",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "VR Chat"
    assert data["slug"] == "vr-chat"


@pytest.mark.asyncio
async def test_list_domains(client: AsyncClient):
    """Test listing domains."""
    # Create a domain first
    await client.post(
        "/api/v1/domains",
        json={
            "name": "VR Code",
            "slug": "vr-code",
        },
    )

    response = await client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_domain(client: AsyncClient):
    """Test getting a domain by ID."""
    # Create a domain
    create_response = await client.post(
        "/api/v1/domains",
        json={
            "name": "VR Lex",
            "slug": "vr-lex",
        },
    )
    domain_id = create_response.json()["id"]

    # Get domain
    response = await client.get(f"/api/v1/domains/{domain_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == domain_id
    assert data["name"] == "VR Lex"

