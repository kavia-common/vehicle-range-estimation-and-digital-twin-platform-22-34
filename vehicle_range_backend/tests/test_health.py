from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Healthy"
    assert "app" in data
    assert "version" in data
