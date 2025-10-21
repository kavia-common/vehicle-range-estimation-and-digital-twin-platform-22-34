from fastapi import APIRouter
from src.domain.schemas import AnalyticsRequest, AnalyticsResponse
from src.services.analytics_service import AnalyticsService

router = APIRouter()
service = AnalyticsService()

# PUBLIC_INTERFACE
@router.post(
    "/run",
    response_model=AnalyticsResponse,
    summary="Run analytics on telemetry efficiency history",
    description="Compute degradation heuristic, trend via least squares, and anomaly indices via z-score.",
)
def run_analytics(req: AnalyticsRequest) -> AnalyticsResponse:
    """Run analytics on efficiency history."""
    return service.run(req)
