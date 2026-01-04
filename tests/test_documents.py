"""Tests for document endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient):
    """Test uploading a document."""
    # First create a domain
    domain_response = await client.post(
        "/api/v1/domains",
        json={
            "name": "Test Domain",
            "slug": "test-domain",
        },
    )
    domain_id = domain_response.json()["id"]

    # Upload document
    files = {"file": ("test.txt", b"Test content", "text/plain")}
    response = await client.post(
        f"/api/v1/documents/upload?domain_id={domain_id}",
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["domain_id"] == domain_id
    assert data["status"] == "uploaded"

