from fastapi import APIRouter
from src.domain.schemas import RangeEstimateRequest, RangeEstimateResponse
from src.services.estimation_service import EstimationService

router = APIRouter()
service = EstimationService()

# PUBLIC_INTERFACE
@router.post(
    "/estimate",
    response_model=RangeEstimateResponse,
    summary="Estimate vehicle range",
    description="Estimate remaining driving range based on vehicle spec and current telemetry.",
)
def estimate_range(payload: RangeEstimateRequest) -> RangeEstimateResponse:
    """Estimate the range using a lightweight energy model."""
    return service.estimate(payload)
