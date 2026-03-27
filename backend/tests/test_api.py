import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def jwt_token():
    token = jwt.encode(
        {"sub": "1", "username": "testuser", "role": "admin"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return token


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data


class TestConversationsEndpoint:
    def test_get_conversations_requires_auth(self, client):
        response = client.get("/api/conversations")
        assert response.status_code == 422

    def test_get_conversations_with_auth(self, client, api_key):
        response = client.get(
            "/api/conversations",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_conversations_pagination(self, client, api_key):
        response = client.get(
            "/api/conversations?skip=0&limit=10",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200


class TestMappingsEndpoints:
    def test_get_channels(self, client, api_key):
        response = client.get(
            "/api/channels",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_agents(self, client, api_key):
        response = client.get(
            "/api/agents",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_teams(self, client, api_key):
        response = client.get(
            "/api/teams",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestLifecyclesEndpoint:
    def test_get_lifecycles_requires_auth(self, client):
        response = client.get("/api/lifecycles")
        assert response.status_code == 422

    def test_get_lifecycles_with_auth(self, client, api_key):
        response = client.get(
            "/api/lifecycles",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200


class TestAdsEndpoint:
    def test_get_ads_requires_auth(self, client):
        response = client.get("/api/ads")
        assert response.status_code == 422

    def test_get_ads_with_auth(self, client, api_key):
        response = client.get(
            "/api/ads",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200


class TestCSATEndpoint:
    def test_get_csat_requires_auth(self, client):
        response = client.get("/api/csat")
        assert response.status_code == 422

    def test_get_csat_with_auth(self, client, api_key):
        response = client.get(
            "/api/csat",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200


class TestImportEndpoint:
    def test_get_template_requires_auth(self, client):
        response = client.get("/api/import/templates/closed_conversations")
        assert response.status_code == 422

    def test_get_template_with_auth(self, client, api_key):
        response = client.get(
            "/api/import/templates/closed_conversations",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert "spreadsheet_type" in data
        assert "columns" in data

    def test_import_rejects_invalid_file_type(self, client, api_key, jwt_token):
        response = client.post(
            "/api/import/closed_conversations",
            headers={"X-API-Key": api_key, "Authorization": f"Bearer {jwt_token}"},
            files={"file": ("test.txt", b"test content", "text/plain")},
        )
        assert response.status_code == 400
