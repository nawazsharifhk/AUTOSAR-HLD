import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "AutoHLD-AI"
    assert data["status"] == "online"


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs():
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
