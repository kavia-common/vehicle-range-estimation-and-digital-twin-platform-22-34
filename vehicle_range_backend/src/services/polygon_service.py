import math
from typing import List, Tuple
from src.domain.schemas import PolygonRequest, PolygonResponse, CircleRequest

EARTH_RADIUS_M = 6371000.0

def _to_ring(coords: List[Tuple[float, float]]) -> List[List[List[float]]]:
    # GeoJSON polygon requires closed ring
    if coords[0] != coords[-1]:
        coords = coords + [coords[0]]
    return [[ [lon, lat] for lon, lat in coords ]]

class PolygonService:
    """Geospatial polygon utilities."""

    def _offset(self, lat: float, lon: float, dx_m: float, dy_m: float) -> Tuple[float, float]:
        d_lat = (dy_m / EARTH_RADIUS_M) * (180.0 / math.pi)
        d_lon = (dx_m / (EARTH_RADIUS_M * math.cos(math.radians(lat)))) * (180.0 / math.pi)
        return lat + d_lat, lon + d_lon

    # PUBLIC_INTERFACE
    def circle(self, req: CircleRequest) -> PolygonResponse:
        """Approximate geodesic circle by sampling around center."""
        lat0, lon0, r = req.center_lat, req.center_lon, req.radius_m
        n = req.points
        pts: List[Tuple[float, float]] = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            dx = r * math.cos(theta)
            dy = r * math.sin(theta)
            lat, lon = self._offset(lat0, lon0, dx, dy)
            pts.append((lon, lat))  # store as (lon, lat)
        return PolygonResponse(type="Polygon", coordinates=_to_ring(pts))

    # PUBLIC_INTERFACE
    def convex_hull(self, req: PolygonRequest) -> PolygonResponse:
        """Monotone chain convex hull for [lon,lat] points."""
        points = [(p[0], p[1]) for p in req.coordinates]
        # Remove duplicates and sort
        points = sorted(set(points))
        if len(points) <= 1:
            ring = _to_ring(points or [(0.0, 0.0)])
            return PolygonResponse(type="Polygon", coordinates=ring)

        def cross(o, a, b):
            return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

        lower: List[Tuple[float, float]] = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper: List[Tuple[float, float]] = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        hull = lower[:-1] + upper[:-1]
        if len(hull) < 3:
            # Degenerate hull -> line/point: create minimal triangle-like ring by repeating points
            hull = hull + hull[: max(0, 3 - len(hull))]
        return PolygonResponse(type="Polygon", coordinates=_to_ring(hull))
