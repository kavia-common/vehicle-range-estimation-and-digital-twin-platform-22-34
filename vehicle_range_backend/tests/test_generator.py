import os
import shutil
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.config import get_settings, ensure_data_dirs

client = TestClient(app)

def setup_module(module):
    # Clean data dir for isolated test
    s = get_settings()
    base = os.path.abspath(s.DATA_DIR)
    if os.path.exists(base):
        shutil.rmtree(base)
    ensure_data_dirs()

def test_generator_deterministic_seed_and_count():
    req = {"scenario": "urban", "minutes": 30, "seed": 123, "export_csv": False}
    r1 = client.post("/generator/telemetry", json=req)
    r2 = client.post("/generator/telemetry", json=req)
    assert r1.status_code == 200 and r2.status_code == 200
    d1, d2 = r1.json(), r2.json()
    assert d1["count"] == 30 and d2["count"] == 30
    # deterministic: compare first few points
    for i in range(5):
        assert d1["points"][i] == d2["points"][i]

def test_generator_export_csv():
    req = {"scenario": "highway", "minutes": 10, "seed": 42, "export_csv": True}
    r = client.post("/generator/telemetry", json=req)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 10
    assert data["export_path"] is not None
    assert os.path.exists(data["export_path"])
