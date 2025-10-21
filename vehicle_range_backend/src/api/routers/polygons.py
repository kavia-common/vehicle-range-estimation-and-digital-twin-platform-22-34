from fastapi import APIRouter
from src.domain.schemas import PolygonRequest, PolygonResponse, CircleRequest
from src.services.polygon_service import PolygonService

router = APIRouter()
service = PolygonService()

# PUBLIC_INTERFACE
@router.post(
    "/range-circle",
    response_model=PolygonResponse,
    summary="Generate approximate geodesic circle polygon",
    description="Create a polygon approximating a geodesic circle around a coordinate with given radius.",
)
def range_circle(req: CircleRequest) -> PolygonResponse:
    """Generate an approximate geodesic circle polygon."""
    return service.circle(req)

# PUBLIC_INTERFACE
@router.post(
    "/convex-hull",
    response_model=PolygonResponse,
    summary="Compute convex hull polygon",
    description="Compute a convex hull for the provided coordinates using monotone chain algorithm.",
)
def convex_hull(req: PolygonRequest) -> PolygonResponse:
    """Compute the convex hull polygon."""
    return service.convex_hull(req)
