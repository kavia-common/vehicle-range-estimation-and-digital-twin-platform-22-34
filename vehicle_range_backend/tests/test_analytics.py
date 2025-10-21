from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_analytics_run_basic():
    series = [6.0, 6.1, 6.2, 6.0, 5.9, 6.3, 6.1, 5.8, 6.2, 6.0]
    r = client.post("/analytics/run", json={"efficiency_history_km_per_kwh": series})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == len(series)
    assert "mean_efficiency" in data
    assert "std_efficiency" in data
    assert "degradation_index" in data
    assert "trend_slope" in data
    assert isinstance(data["anomalies_idx"], list)
