"""
Test para LegacyGcodeGeneratorAdapter
"""
from infrastructure.adapters.legacy_gcode_generator_adapter import LegacyGcodeGeneratorAdapter
from svgpathtools import Path, Line

def test_legacy_gcode_generator_adapter_generate():
    # Crear un path SVG real compatible
    path = Path(Line(0+0j, 10+0j), Line(10+0j, 10+10j))
    paths = [path]
    svg_attr = {"viewBox": "0 0 10 10"}
    # Instanciar con parámetros mínimos
    adapter = LegacyGcodeGeneratorAdapter(
        feed=1000,
        cmd_down="M3 S1000",
        cmd_up="M5",
        step_mm=1.0,
        dwell_ms=0,
        max_height_mm=10.0,
        logger=None,
        transform_strategies=[]
    )
    gcode = adapter.generate(paths, svg_attr)
    assert isinstance(gcode, list)
    assert any("G1" in line or "G0" in line for line in gcode)
