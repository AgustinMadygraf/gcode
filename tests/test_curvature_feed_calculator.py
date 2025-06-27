import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

"""
Test manual mínimo para CurvatureFeedCalculator y refactor en GCodeGeneratorAdapter.
"""
from adapters.output.feed_rate_strategy import FeedRateStrategy
from adapters.output.curvature_feed_calculator import CurvatureFeedCalculator

class DummyPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_curvature_feed():
    strategy = FeedRateStrategy(base_feed=1000, curvature_factor=0.3, min_feed_factor=0.5)
    calc = CurvatureFeedCalculator(strategy)
    p1 = DummyPoint(0, 0)
    p2 = DummyPoint(1, 0)
    p3 = DummyPoint(1, 1)
    feed = calc.adjust_feed(p1, p2, p3)
    print(f"Feed calculado (curva 90°): {feed}")
    assert 500 <= feed <= 1000
    # Caso línea recta
    p4 = DummyPoint(2, 0)
    feed2 = calc.adjust_feed(p1, p2, p4)
    print(f"Feed calculado (línea recta): {feed2}")
    assert abs(feed2 - 1000) < 1

if __name__ == "__main__":
    test_curvature_feed()
    print("OK")
