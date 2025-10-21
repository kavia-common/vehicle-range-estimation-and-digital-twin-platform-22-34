import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.core.config import get_settings, ensure_data_dirs
from src.domain.schemas import DigitalTwinCreate, DigitalTwin, DigitalTwinUpdate, TwinListResponse

class TwinService:
    """File-based JSON persistence for digital twins."""

    def __init__(self) -> None:
        ensure_data_dirs()
        self.base = os.path.abspath(get_settings().DATA_DIR)
        self.twin_dir = os.path.join(self.base, "twins")

    def _path(self, twin_id: str) -> str:
        safe = "".join(ch for ch in twin_id if ch.isalnum() or ch in ("-", "_"))
        return os.path.join(self.twin_dir, f"{safe}.json")

    def _load(self, path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, path: str, data: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    # PUBLIC_INTERFACE
    def create(self, payload: DigitalTwinCreate) -> DigitalTwin:
        """Create and persist a twin."""
        _id = str(uuid.uuid4())
        now = datetime.utcnow()
        record = {
            "id": _id,
            "name": payload.name,
            "vehicle": payload.vehicle.model_dump(),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        self._save(self._path(_id), record)
        return DigitalTwin(**record)

    # PUBLIC_INTERFACE
    def get(self, twin_id: str) -> Optional[DigitalTwin]:
        """Get a twin by ID."""
        data = self._load(self._path(twin_id))
        if data is None:
            return None
        return DigitalTwin(**data)

    # PUBLIC_INTERFACE
    def list(self, offset: int = 0, limit: int = 50) -> TwinListResponse:
        """List twins with pagination."""
        files = [f for f in os.listdir(self.twin_dir) if f.endswith(".json")]
        files.sort()
        total = len(files)
        sel = files[offset: offset + limit]
        items: List[DigitalTwin] = []
        for fn in sel:
            data = self._load(os.path.join(self.twin_dir, fn))
            if data:
                items.append(DigitalTwin(**data))
        return TwinListResponse(items=items, total=total, offset=offset, limit=limit)

    # PUBLIC_INTERFACE
    def update(self, twin_id: str, update: DigitalTwinUpdate) -> Optional[DigitalTwin]:
        """Update fields of an existing twin."""
        path = self._path(twin_id)
        data = self._load(path)
        if data is None:
            return None
        if update.name is not None:
            data["name"] = update.name
        if update.vehicle is not None:
            data["vehicle"] = update.vehicle.model_dump()
        data["updated_at"] = datetime.utcnow().isoformat()
        self._save(path, data)
        return DigitalTwin(**data)

    # PUBLIC_INTERFACE
    def delete(self, twin_id: str) -> bool:
        """Delete a twin by ID."""
        path = self._path(twin_id)
        if not os.path.exists(path):
            return False
        os.remove(path)
        return True
