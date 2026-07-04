import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient() as http_client:
        app.state.http_client = http_client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_admin_health_endpoint(client):
    resp = await client.get("/api/v1/admin/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "database" in data["checks"]
    assert "version" in data
    assert "uptime_seconds" in data
