from typing import Dict
from src.domain.schemas import RangeEstimateRequest, RangeEstimateResponse

class EstimationService:
    """Lightweight estimation without external dependencies."""

    def _efficiency_adjustment(self, speed_kmh: float, temperature_c: float, wind_kmh: float) -> float:
        """
        Base efficiency nominal: 6.0 km/kWh (generic EV).
        Adjust:
          - Speed: efficiency degrades after 90km/h by 0.02 per km/h over 90, improves under 50 by +0.01 per km/h diff
          - Temperature: away from 20C reduces 0.02 per degree magnitude
          - Headwind: reduces 0.01 per km/h of headwind, tailwind improves 0.005 per km/h
        Clamp final efficiency in [2.0, 9.0].
        """
        eff = 6.0
        if speed_kmh > 90:
            eff -= 0.02 * (speed_kmh - 90)
        elif speed_kmh < 50:
            eff += 0.01 * (50 - speed_kmh)

        eff -= 0.02 * abs(temperature_c - 20)

        if wind_kmh >= 0:
            eff -= 0.01 * wind_kmh
        else:
            eff += 0.005 * abs(wind_kmh)

        return max(2.0, min(9.0, eff))

    # PUBLIC_INTERFACE
    def estimate(self, req: RangeEstimateRequest) -> RangeEstimateResponse:
        """Estimate range based on available energy and efficiency adjustments."""
        v = req.vehicle
        t = req.telemetry

        usable_kwh = v.battery_kwh * (t.soc_percent * 0.01) * (1 - v.reserve_percent * 0.01)
        usable_kwh = max(0.0, usable_kwh)

        efficiency = self._efficiency_adjustment(t.speed_kmh, t.temperature_c, t.wind_kmh)

        estimated_km = usable_kwh * efficiency

        assumptions: Dict[str, float] = {
            "usable_kwh": round(usable_kwh, 3),
            "efficiency_km_per_kwh": round(efficiency, 3),
        }
        return RangeEstimateResponse(estimated_km=round(estimated_km, 3), assumptions=assumptions)
