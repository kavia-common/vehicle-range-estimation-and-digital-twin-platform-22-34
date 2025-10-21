from fastapi import APIRouter
from src.domain.schemas import SyntheticDataRequest, SyntheticDataResponse
from src.services.generator_service import GeneratorService

router = APIRouter()
service = GeneratorService()

# PUBLIC_INTERFACE
@router.post(
    "/telemetry",
    response_model=SyntheticDataResponse,
    summary="Generate synthetic telemetry",
    description="Generate deterministic telemetry series for scenarios (urban/highway/mixed). Optionally export CSV.",
)
def generate(req: SyntheticDataRequest) -> SyntheticDataResponse:
    """Generate synthetic telemetry data."""
    return service.generate(req)
