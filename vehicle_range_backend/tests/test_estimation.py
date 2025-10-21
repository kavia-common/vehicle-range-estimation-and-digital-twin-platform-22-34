from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

base_vehicle = {
    "make": "Make",
    "model": "Model",
    "year": 2022,
    "battery_kwh": 75,
    "reserve_percent": 10
}

def test_estimation_basic():
    payload = {
        "vehicle": base_vehicle,
        "telemetry": {"speed_kmh": 80, "temperature_c": 20, "wind_kmh": 0, "soc_percent": 50}
    }
    r = client.post("/estimation/estimate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["estimated_km"] > 0
    assert "assumptions" in data

def test_estimation_edge_zero_soc():
    payload = {
        "vehicle": base_vehicle,
        "telemetry": {"speed_kmh": 80, "temperature_c": 20, "wind_kmh": 0, "soc_percent": 0}
    }
    r = client.post("/estimation/estimate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["estimated_km"] == 0
