import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


from domain.gcode.gcode_border_rectangle_detector import GCodeBorderRectangleDetector
from domain.gcode.gcode_border_filter import GCodeBorderFilter

def test_border_rectangle_detection():
    sample_gcode = """G0 X0.000 Y0.000
G4 P0.350
G0 X0.000 Y250.000
G4 P0.350
M3 S255; baja lapicera
G4 P0.350
G1 X0.000 Y249.885 F4000
G1 X0.000 Y0.000
G1 X155.000 Y0.000
G1 X155.000 Y250.000
G1 X0.000 Y250.000
G4 P0.350
M5; sube lapicera
G4 P0.350
G0 X7.692 Y199.615"""
    detector = GCodeBorderRectangleDetector()
    assert detector.detect_border_pattern(sample_gcode.split('\n')) is not None
    print("Detección de borde: OK")

def test_border_filter():
    sample_gcode = """G0 X0.000 Y0.000
G4 P0.350
G0 X0.000 Y250.000
G4 P0.350
M3 S255; baja lapicera
G4 P0.350
G1 X0.000 Y249.885 F4000
G1 X0.000 Y0.000
G1 X155.000 Y0.000
G1 X155.000 Y250.000
G1 X0.000 Y250.000
G4 P0.350
M5; sube lapicera
G4 P0.350
G0 X7.692 Y199.615"""
    detector = GCodeBorderRectangleDetector()
    border_filter = GCodeBorderFilter(detector)
    filtered = border_filter.filter(sample_gcode)
    assert "M3 S255; baja lapicera" not in filtered
    print("Filtrado de borde: OK")

if __name__ == "__main__":
    test_border_rectangle_detection()
    test_border_filter()
