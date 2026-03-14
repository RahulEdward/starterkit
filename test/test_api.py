"""
API Endpoint Tests
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
