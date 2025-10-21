from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, conlist, confloat
from datetime import datetime

def _validate_lat(value: float) -> float:
    if value < -90 or value > 90:
        raise ValueError("Latitude must be between -90 and 90")
    return value

def _validate_lon(value: float) -> float:
    if value < -180 or value > 180:
        raise ValueError("Longitude must be between -180 and 180")
    return value

class VehicleSpec(BaseModel):
    make: str = Field(..., description="Vehicle make")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Model year", ge=1980, le=2100)
    battery_kwh: float = Field(..., description="Battery capacity in kWh", gt=0)
    reserve_percent: float = Field(10.0, description="Reserve buffer percent", ge=0, le=50)

class Telemetry(BaseModel):
    speed_kmh: float = Field(..., description="Current speed (km/h)", ge=0, le=300)
    temperature_c: float = Field(..., description="Ambient temperature (C)", ge=-60, le=60)
    wind_kmh: float = Field(0, description="Headwind (+) or tailwind (-) in km/h", ge=-150, le=150)
    soc_percent: float = Field(..., description="State of charge percent", ge=0, le=100)

class RangeEstimateRequest(BaseModel):
    vehicle: VehicleSpec
    telemetry: Telemetry

class RangeEstimateResponse(BaseModel):
    estimated_km: float
    assumptions: dict

class CircleRequest(BaseModel):
    center_lat: float = Field(..., description="Center latitude")
    center_lon: float = Field(..., description="Center longitude")
    radius_m: float = Field(..., description="Radius in meters", gt=0)
    points: int = Field(64, description="Number of points for polygon", ge=12, le=512)

    _lat_check = field_validator("center_lat")(_validate_lat)
    _lon_check = field_validator("center_lon")(_validate_lon)

class PolygonRequest(BaseModel):
    coordinates: conlist(conlist(confloat(), min_length=2, max_length=2), min_length=3, max_length=10000) = Field(
        ..., description="List of [lon, lat] pairs"
    )

class PolygonResponse(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]]  # ring list -> [ [ [lon,lat], ... ] ]

class DigitalTwinBase(BaseModel):
    name: str = Field(..., description="Twin name", min_length=1, max_length=200)
    vehicle: VehicleSpec

class DigitalTwinCreate(DigitalTwinBase):
    pass

class DigitalTwinUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Twin name", min_length=1, max_length=200)
    vehicle: Optional[VehicleSpec] = None

class DigitalTwin(DigitalTwinBase):
    id: str = Field(..., description="Twin ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class TwinListResponse(BaseModel):
    items: List[DigitalTwin]
    total: int
    offset: int
    limit: int

class AnalyticsRequest(BaseModel):
    efficiency_history_km_per_kwh: conlist(confloat(gt=0, lt=20), min_length=5, max_length=10000)

class AnalyticsResponse(BaseModel):
    count: int
    mean_efficiency: float
    std_efficiency: float
    degradation_index: float
    trend_slope: float
    trend_intercept: float
    anomalies_idx: List[int]

class SyntheticDataRequest(BaseModel):
    scenario: Literal["urban", "highway", "mixed"] = Field(..., description="Driving scenario")
    minutes: int = Field(60, description="Duration in minutes", ge=5, le=10080)
    seed: Optional[int] = Field(None, description="Deterministic seed")
    export_csv: bool = Field(False, description="Export CSV to data/exports")

class SyntheticDataPoint(BaseModel):
    t: int
    speed_kmh: float
    temperature_c: float
    wind_kmh: float
    soc_percent: float

class SyntheticDataResponse(BaseModel):
    points: List[SyntheticDataPoint]
    count: int
    export_path: Optional[str] = None
