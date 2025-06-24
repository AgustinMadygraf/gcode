"""
Test de integración: flujo completo SVG → G-code
"""
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from domain.gcode_generator import GcodeGenerator, GCodeGenerationService


def test_svg_to_gcode(tmp_path):
    # SVG de prueba mínimo
    svg_content = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M0,0 L10,0 L10,10 Z"/></svg>'''
    svg_file = tmp_path / "test.svg"
    svg_file.write_text(svg_content, encoding="utf-8")

    # Loader
    loader = SvgLoaderAdapter(svg_file)
    paths = loader.get_paths()
    attrs = loader.get_attributes()

    # Generador
    generator = GcodeGenerator(
        feed=1000,
        cmd_down="M3 S1000",
        cmd_up="M5",
        step_mm=1.0,
        dwell_ms=0,
        max_height_mm=10.0,
        logger=None,
        transform_strategies=[]
    )
    gcode_service = GCodeGenerationService(generator)
    gcode = gcode_service.generate(paths, attrs)
    assert isinstance(gcode, list)
    assert any("G1" in line or "G0" in line for line in gcode)
    # Guardar G-code generado
    gcode_file = tmp_path / "test.gcode"
    gcode_file.write_text("\n".join(gcode), encoding="utf-8")
    assert gcode_file.exists()
    assert gcode_file.stat().st_size > 0
