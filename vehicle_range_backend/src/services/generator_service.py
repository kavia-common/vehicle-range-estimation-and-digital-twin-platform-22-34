import os
import csv
import random
import uuid
from typing import List, Tuple
from src.core.config import get_settings, ensure_data_dirs
from src.domain.schemas import SyntheticDataRequest, SyntheticDataResponse, SyntheticDataPoint

class GeneratorService:
    """Deterministic synthetic telemetry generator."""

    def __init__(self) -> None:
        ensure_data_dirs()
        base = os.path.abspath(get_settings().DATA_DIR)
        self.export_dir = os.path.join(base, "exports")

    def _profile(self, scenario: str, t: int, rng: random.Random) -> Tuple[float, float, float, float]:
        """
        Return (speed_kmh, temp_c, wind_kmh, soc_percent).
        - speed varies with scenario:
            urban: 0-60 with stop-and-go
            highway: 80-120 steady
            mixed: blend
        - temp slowly drifts around 20C
        - wind small noise
        - soc decreases steadily with small noise
        """
        if scenario == "urban":
            base_speed = 30 + 20 * (rng.random() - 0.5)  # around 30
            # stop-and-go pattern
            if (t // 5) % 2 == 0:
                base_speed *= 0.3
        elif scenario == "highway":
            base_speed = 100 + 10 * (rng.random() - 0.5)
        else:  # mixed
            base_speed = 60 + 30 * (rng.random() - 0.5)

        temp = 20 + 5 * (rng.random() - 0.5)
        wind = 5 * (rng.random() - 0.5)

        # Simple soc drain: about 0.05% per minute at moderate usage
        soc = max(0.0, 100.0 - 0.05 * t + 0.01 * (rng.random() - 0.5) * t / 10.0)
        return max(0.0, base_speed), temp, wind, soc

    # PUBLIC_INTERFACE
    def generate(self, req: SyntheticDataRequest) -> SyntheticDataResponse:
        """Generate telemetry time series; optionally export CSV."""
        rng = random.Random(req.seed) if req.seed is not None else random.Random(42)
        points: List[SyntheticDataPoint] = []
        for i in range(req.minutes):
            s, temp, wind, soc = self._profile(req.scenario, i, rng)
            points.append(
                SyntheticDataPoint(
                    t=i,
                    speed_kmh=round(s, 3),
                    temperature_c=round(temp, 3),
                    wind_kmh=round(wind, 3),
                    soc_percent=round(soc, 3),
                )
            )

        export_path = None
        if req.export_csv:
            ensure_data_dirs()
            fname = f"{uuid.uuid4()}.csv"
            export_path = os.path.join(self.export_dir, fname)
            with open(export_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["t", "speed_kmh", "temperature_c", "wind_kmh", "soc_percent"])
                for p in points:
                    w.writerow([p.t, p.speed_kmh, p.temperature_c, p.wind_kmh, p.soc_percent])

        return SyntheticDataResponse(points=points, count=len(points), export_path=export_path)
