"""
CurvatureFeedCalculator: encapsula el cálculo de curvatura y ajuste de feed-rate para G-code.
"""
from typing import Optional
import math

class CurvatureFeedCalculator:
    def __init__(self, feed_rate_strategy):
        self.feed_rate_strategy = feed_rate_strategy

    def calculate_curvature(self, p1, p2, p3) -> Optional[float]:
        if p1 is None or p2 is None or p3 is None:
            return None
        v1 = (p2.x - p1.x, p2.y - p1.y)
        v2 = (p3.x - p2.x, p3.y - p2.y)
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 < 1e-6 or mag2 < 1e-6:
            return None
        dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)
        angle_deg = math.degrees(angle)
        curvature = angle_deg / 180
        return curvature

    def adjust_feed(self, p1, p2, p3) -> float:
        curvature = self.calculate_curvature(p1, p2, p3)
        return self.feed_rate_strategy.adjust_feed(curvature=curvature)
