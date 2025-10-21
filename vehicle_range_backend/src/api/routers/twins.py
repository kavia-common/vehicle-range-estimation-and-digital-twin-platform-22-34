from fastapi import APIRouter, HTTPException
from src.domain.schemas import DigitalTwinCreate, DigitalTwin, DigitalTwinUpdate, TwinListResponse
from src.services.twin_service import TwinService

router = APIRouter()
service = TwinService()

# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=DigitalTwin,
    summary="Create digital twin",
    description="Create a digital twin persisted as a JSON file.",
)
def create_twin(twin: DigitalTwinCreate) -> DigitalTwin:
    """Create a digital twin."""
    return service.create(twin)

# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=TwinListResponse,
    summary="List digital twins",
    description="List digital twins with pagination.",
)
def list_twins(offset: int = 0, limit: int = 50) -> TwinListResponse:
    """List twins with offset/limit pagination."""
    return service.list(offset=offset, limit=limit)

# PUBLIC_INTERFACE
@router.get(
    "/{twin_id}",
    response_model=DigitalTwin,
    summary="Get digital twin",
    description="Retrieve a single digital twin by ID.",
)
def get_twin(twin_id: str) -> DigitalTwin:
    """Get a twin by ID."""
    twin = service.get(twin_id)
    if twin is None:
        raise HTTPException(status_code=404, detail="Twin not found")
    return twin

# PUBLIC_INTERFACE
@router.put(
    "/{twin_id}",
    response_model=DigitalTwin,
    summary="Update digital twin",
    description="Update an existing digital twin by ID.",
)
def update_twin(twin_id: str, update: DigitalTwinUpdate) -> DigitalTwin:
    """Update a twin."""
    result = service.update(twin_id, update)
    if result is None:
        raise HTTPException(status_code=404, detail="Twin not found")
    return result

# PUBLIC_INTERFACE
@router.delete(
    "/{twin_id}",
    response_model=dict,
    summary="Delete digital twin",
    description="Delete a digital twin by ID.",
)
def delete_twin(twin_id: str) -> dict:
    """Delete a twin by ID."""
    ok = service.delete(twin_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Twin not found")
    return {"deleted": True, "id": twin_id}
