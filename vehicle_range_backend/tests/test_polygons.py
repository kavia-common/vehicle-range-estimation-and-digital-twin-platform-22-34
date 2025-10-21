from fastapi.testclient import TestClient
from src.api.main import app
import math

client = TestClient(app)

def test_range_circle_polygon():
    payload = {"center_lat": 37.0, "center_lon": -122.0, "radius_m": 1000, "points": 36}
    r = client.post("/polygons/range-circle", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "Polygon"
    ring = data["coordinates"][0]
    # closed ring
    assert ring[0] == ring[-1]
    # number of vertices equals points + 1 (closed)
    assert len(ring) == payload["points"] + 1
    # approximate radius check for first point east
    lon0, lat0 = payload["center_lon"], payload["center_lat"]
    lon1, lat1 = ring[0]
    # haversine approx
    def haversine(lat_a, lon_a, lat_b, lon_b):
        R = 6371000.0
        dlat = math.radians(lat_b - lat_a)
        dlon = math.radians(lon_b - lon_a)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat_a))*math.cos(math.radians(lat_b))*math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    d = haversine(lat0, lon0, lat1, lon1)
    assert abs(d - payload["radius_m"]) < 200  # within 200m tolerance

def test_convex_hull():
    coords = [[0,0],[1,0],[1,1],[0,1],[0.5,0.5]]
    r = client.post("/polygons/convex-hull", json={"coordinates": coords})
    assert r.status_code == 200
    data = r.json()
    ring = data["coordinates"][0]
    # first 4 unique points should form a square hull (order may vary but size >= 4 including closing point)
    assert len(ring) >= 5
