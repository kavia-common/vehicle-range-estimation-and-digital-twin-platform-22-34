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

def test_twin_crud_and_persistence():
    twin = {
        "name": "My Twin",
        "vehicle": {"make":"A","model":"B","year":2023,"battery_kwh":60,"reserve_percent":10}
    }
    r = client.post("/twins", json=twin)
    assert r.status_code == 200
    created = r.json()
    twin_id = created["id"]

    # get
    r = client.get(f"/twins/{twin_id}")
    assert r.status_code == 200

    # list
    r = client.get("/twins?offset=0&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    # update
    r = client.put(f"/twins/{twin_id}", json={"name": "Updated Twin"})
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Twin"

    # delete
    r = client.delete(f"/twins/{twin_id}")
    assert r.status_code == 200

    # ensure gone
    r = client.get(f"/twins/{twin_id}")
    assert r.status_code == 404
