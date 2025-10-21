from typing import List
from math import sqrt
from src.domain.schemas import AnalyticsRequest, AnalyticsResponse

class AnalyticsService:
    """Compute basic analytics without external libs."""

    def _mean(self, xs: List[float]) -> float:
        return sum(xs) / len(xs)

    def _std(self, xs: List[float], mean: float) -> float:
        if len(xs) < 2:
            return 0.0
        var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
        return sqrt(var)

    def _trend(self, xs: List[float]) -> (float, float):
        # y = a*x + b, x = 0..n-1
        n = len(xs)
        if n == 0:
            return 0.0, 0.0
        sx = sum(range(n))
        sy = sum(xs)
        sxx = sum(i * i for i in range(n))
        sxy = sum(i * xs[i] for i in range(n))
        denom = (n * sxx - sx * sx)
        if denom == 0:
            return 0.0, xs[0]
        a = (n * sxy - sx * sy) / denom
        b = (sy - a * sx) / n
        return a, b

    # PUBLIC_INTERFACE
    def run(self, req: AnalyticsRequest) -> AnalyticsResponse:
        """Compute degradation heuristic, trend via least squares, anomaly detection via z-score."""
        xs = list(req.efficiency_history_km_per_kwh)
        mean = self._mean(xs)
        std = self._std(xs, mean)
        slope, intercept = self._trend(xs)
        # Degradation heuristic: negative slope normalized by mean (clip)
        degradation = max(-1.0, min(1.0, -slope / (mean if mean else 1.0)))

        anomalies = []
        if std > 0:
            for i, x in enumerate(xs):
                z = abs((x - mean) / std)
                if z > 2.5:
                    anomalies.append(i)

        return AnalyticsResponse(
            count=len(xs),
            mean_efficiency=round(mean, 6),
            std_efficiency=round(std, 6),
            degradation_index=round(degradation, 6),
            trend_slope=round(slope, 6),
            trend_intercept=round(intercept, 6),
            anomalies_idx=anomalies,
        )
