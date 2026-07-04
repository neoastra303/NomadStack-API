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
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_returns_html(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_search_no_api_key_returns_502(client):
    resp = await client.get("/api/v1/search?city=London")
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_compare_no_api_key_returns_empty(client):
    resp = await client.get("/api/v1/compare?cities=London,Paris")
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []


@pytest.mark.asyncio
async def test_forecast_no_api_key_returns_502(client):
    resp = await client.get("/api/v1/forecast?city=London")
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_auth_register_missing_fields(client):
    resp = await client.post("/api/v1/auth/register", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_auth_login_missing_fields(client):
    resp = await client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_profile_no_auth(client):
    resp = await client.get("/api/v1/auth/profile")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_favorites_no_auth(client):
    resp = await client.get("/api/v1/me/favorites")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_history_no_auth(client):
    resp = await client.get("/api/v1/me/history")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_openapi_docs(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert len(data["paths"]) >= 10
