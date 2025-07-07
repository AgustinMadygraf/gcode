import pytest
from infrastructure.adapters.reference_marks_generator import ReferenceMarkBlockGenerator

def test_reference_mark_block_generator_basic():
    """
    Testea que ReferenceMarkBlockGenerator genera las marcas de referencia principales y los movimientos en L.
    """
    feed = 1000
    cmd_down = "M3 S255"
    cmd_up = "M5"
    dwell = 100
    width = 210.0
    height = 148.0
    generator = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True)
    gcode_lines = generator.generate(width, height)
    # Verifica que haya movimientos a las posiciones esperadas (según lógica de reference_mark_gcode)
    assert any("G0 X0 Y5" in line for line in gcode_lines)
    assert any(f"G0 X{width} Y5" in line for line in gcode_lines)
    assert any(f"G0 X{width} Y{height-5}" in line for line in gcode_lines)
    assert any(f"G0 X0 Y{height-5}" in line for line in gcode_lines)
    # Verifica que existan los movimientos en L
    assert any("; Movimiento horizontal por borde inferior" in line for line in gcode_lines)
    assert any("; Movimiento vertical por borde derecho" in line for line in gcode_lines)
    assert any("; Movimiento horizontal por borde superior" in line for line in gcode_lines)
    # Verifica que los comandos de bajada y subida estén presentes
    assert cmd_down in gcode_lines
    assert cmd_up in gcode_lines
    # Verifica que haya comandos DWELL
    assert any("G4 P" in line for line in gcode_lines)
