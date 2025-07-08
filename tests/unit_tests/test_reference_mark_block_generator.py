from infrastructure.adapters.reference_marks_generator import ReferenceMarkBlockGenerator, ReferenceMarkGenerator

def test_reference_mark_generator_single():
    """
    Testea que ReferenceMarkGenerator genera correctamente una marca individual.
    """
    feed = 1000
    cmd_down = "M3 S255"
    cmd_up = "M5"
    dwell = 100
    gen = ReferenceMarkGenerator(feed, cmd_down, cmd_up, dwell)
    lines = gen.generate(0, 0, 'bottomleft')
    # Debe contener los comandos de bajada, subida y dwell
    assert cmd_down in lines
    assert cmd_up in lines
    assert any("G4 P" in l for l in lines)
    # Debe contener movimientos G0 y G1
    assert any(l.startswith("G0 ") for l in lines)
    assert any(l.startswith("G1 ") for l in lines)

def test_reference_mark_block_generator_basic():
    """
    Testea que ReferenceMarkBlockGenerator orquesta marcas y transiciones correctamente.
    """
    feed = 1000
    cmd_down = "M3 S255"
    cmd_up = "M5"
    dwell = 100
    width = 210.0
    height = 148.0
    generator = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True)
    gcode_lines = generator.generate(width, height)
    # Verifica que existan las transiciones correctas
    assert f"G0 X{width} Y0" in gcode_lines
    assert f"G0 X{width} Y{height}" in gcode_lines
    assert f"G0 X0 Y{height}" in gcode_lines
    assert "G0 X0 Y0" in gcode_lines
    # Verifica que los comandos de bajada y subida estén presentes
    assert cmd_down in gcode_lines
    assert cmd_up in gcode_lines
    # Verifica que haya comandos DWELL
    assert any("G4 P" in line for line in gcode_lines)

def test_reference_mark_block_generator_extremo_literal():
    """
    Testea que ReferenceMarkBlockGenerator orquesta marcas y transiciones de extremo literal correctamente.
    """
    feed = 1000
    cmd_down = "M3 S255"
    cmd_up = "M5"
    dwell = 100
    width = 210.0
    height = 148.0
    generator = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True)
    gcode_lines = generator.generate(width, height)
    # Verifica que existan las transiciones de extremo literal
    assert f"G0 X0 Y{height}" in gcode_lines
    assert f"G0 X{width} Y{height}" in gcode_lines
    assert f"G0 X{width} Y0" in gcode_lines
    assert "G0 X0 Y0" in gcode_lines
    # Verifica que los comandos de bajada y subida estén presentes
    assert cmd_down in gcode_lines
    assert cmd_up in gcode_lines
    # Verifica que haya comandos DWELL
    assert any("G4 P" in line for line in gcode_lines)

def test_reference_mark_block_generator_four_marks_with_comments(monkeypatch):
    """
    Verifica que se generan cuatro marcas de referencia con los comentarios correctos y en las esquinas de TARGET_WRITE_AREA_MM.
    """
    feed = 1000
    cmd_down = "M3 S255"
    cmd_up = "M5"
    dwell = 100
    width = 210.0
    height = 148.0
    # Mock de config para TARGET_WRITE_AREA_MM
    class DummyConfig:
        def get(self, k, d=None):
            if k == 'TARGET_WRITE_AREA_MM':
                return [123.0, 77.0]
            return d
    monkeypatch.setattr('infrastructure.adapters.reference_marks_generator.Config', DummyConfig)
    generator = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True)
    gcode_lines = generator.generate(width, height)
    # Verifica comentarios
    for i in range(1, 5):
        assert any(f'Iniciando {i}ra marca de referencia' in l for l in gcode_lines)
    # Verifica posiciones de las marcas (esquinas de TARGET_WRITE_AREA_MM)
    assert any('G0 X0 Y0' in l for l in gcode_lines)  # Marca 1
    assert any('G0 X123.0 Y0' in l for l in gcode_lines)  # Marca 2
    assert any('G0 X123.0 Y77.0' in l for l in gcode_lines)  # Marca 3
    assert any('G0 X0 Y77.0' in l for l in gcode_lines)  # Marca 4
    # Verifica comandos principales
    assert cmd_down in gcode_lines
    assert cmd_up in gcode_lines
    assert any('G4 P' in l for l in gcode_lines)
