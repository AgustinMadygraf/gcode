"""
Test de integración: flujo completo SVG → G-code usando adaptadores legacy
"""

# TEST OBSOLETO: Este test usaba adaptadores legacy eliminados. Puede eliminarse si ya no se requiere compatibilidad legacy.

def test_svg_to_gcode_legacy_adapters(tmp_path):
    # SVG de prueba mínimo
    svg_content = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M0,0 L10,0 L10,10 Z"/></svg>'''
    svg_file = tmp_path / "test.svg"
    svg_file.write_text(svg_content, encoding="utf-8")

    # Loader legacy
    loader = LegacySvgLoaderAdapter(svg_file)
    loader.load()
    paths = loader.get_paths()
    attrs = loader.get_attributes()

    # Generador legacy
    generator = LegacyGcodeGeneratorAdapter(
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
