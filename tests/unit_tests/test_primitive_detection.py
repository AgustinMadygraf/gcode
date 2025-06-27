import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
print('sys.path:', sys.path)
"""
Test básico para SVGPrimitiveDetector.
"""
from domain.services.primitive_detection import SVGPrimitiveDetector

class DummySegment:
    def __init__(self, radius=None, center=None):
        self.radius = radius
        self.center = center

class DummyPath:
    def __init__(self, segments):
        self.segments = segments


def test_detect_circle():
    seg = DummySegment(radius=(10, 10), center=(5, 5))
    path = DummyPath([seg])
    detector = SVGPrimitiveDetector()
    result = detector.detect(path)
    assert result and result[0]['type'] == 'circle'
    print("Detección de círculo: OK")

def test_detect_ellipse():
    seg = DummySegment(radius=(10, 5), center=(0, 0))
    path = DummyPath([seg])
    detector = SVGPrimitiveDetector()
    result = detector.detect(path)
    assert result and result[0]['type'] == 'ellipse'
    print("Detección de elipse: OK")

if __name__ == "__main__":
    test_detect_circle()
    test_detect_ellipse()
    print("Todos los tests pasaron.")
