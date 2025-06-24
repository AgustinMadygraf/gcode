import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.entities.point import Point
from domain.services.optimization.optimization_chain import OptimizationChain
from adapters.input.path_sampler import PathSampler
from infrastructure.config.config import Config

SVG_SIMPLE_LINE = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M1 1 L9 1"/></svg>'''
SVG_BROKEN_LINE = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M1 1 L5 1 M5.001 1 L9 1"/></svg>'''

config = Config()
# Parámetros mínimos para GCodeGenerator
GEN_KWARGS = dict(
    feed=config.feed,
    cmd_down=config.cmd_down,
    cmd_up=config.cmd_up,
    step_mm=config.step_mm,
    dwell_ms=config.dwell_ms,
    max_height_mm=config.max_height_mm,
    optimizer=OptimizationChain()
)

class DummySegment:
    def __init__(self, start, end):
        self._start = start
        self._end = end
    def point(self, t):
        x = self._start[0] + (self._end[0] - self._start[0]) * t
        y = self._start[1] + (self._end[1] - self._start[1]) * t
        return complex(x, y)
    def length(self):
        x0, y0 = self._start
        x1, y1 = self._end
        return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

def test_single_line_no_duplicate_g1(tmp_path):
    # Guardar SVG temporal
    svg_path = tmp_path / "line.svg"
    svg_path.write_text(SVG_SIMPLE_LINE)
    loader = SvgLoaderAdapter(str(svg_path))
    subpaths = loader.get_subpaths()
    # Usar segmentos mock en vez de Point
    points = [[DummySegment((1, 1), (9, 1))]]
    generator = GCodeGeneratorAdapter(
        path_sampler=PathSampler(1.0),
        config=config,
        **GEN_KWARGS
    )
    gcode_service = GCodeGenerationService(generator)
    gcode = gcode_service.generate(points, {})
    # Debe haber solo un bloque de G1 para la línea
    g1_lines = [l for l in gcode if l.startswith('G1')]
    assert len(g1_lines) >= 1, f"Se esperaba al menos 1 comando G1, se encontraron: {g1_lines}"
    # Verificar presencia de cualquier comando de bajada y subida de herramienta
    assert any(cmd in l for l in gcode for cmd in [config.cmd_down, 'M3 S255', 'M3 S1000']), "Debe haber al menos un comando de bajada de herramienta"
    assert any(cmd in l for l in gcode for cmd in [config.cmd_up, 'M5']), "Debe haber al menos un comando de elevación de herramienta"

def test_broken_line_creates_two_traces(tmp_path):
    svg_path = tmp_path / "broken.svg"
    svg_path.write_text(SVG_BROKEN_LINE)
    loader = SvgLoaderAdapter(str(svg_path))
    subpaths = loader.get_subpaths()
    # Usar segmentos mock para dos trazos
    points = [[DummySegment((1, 1), (5, 1))], [DummySegment((5.001, 1), (9, 1))]]
    gen = GCodeGeneratorAdapter(path_sampler=PathSampler(1.0), config=config, **GEN_KWARGS)
    gcode_service = GCodeGenerationService(gen)
    gcode = gcode_service.generate(points, {})
    # Debe haber dos bloques de G1
    g1_lines = [l for l in gcode if l.startswith('G1')]
    assert len(g1_lines) >= 2, f"Se esperaba al menos 2 comandos G1, se encontraron: {g1_lines}"
    assert sum(cmd in l for l in gcode for cmd in [config.cmd_down, 'M3 S255', 'M3 S1000']) >= 2, "Debe haber al menos dos comandos de bajada de herramienta"
    assert sum(cmd in l for l in gcode for cmd in [config.cmd_up, 'M5']) >= 2, "Debe haber al menos dos comandos de elevación de herramienta"

def test_no_duplicate_points():
    # Simula segmentos con puntos duplicados
    points = [[DummySegment((1, 1), (1, 1)), DummySegment((1, 1), (5, 1)), DummySegment((5, 1), (9, 1)), DummySegment((9, 1), (9, 1))]]
    gen = GCodeGeneratorAdapter(
        path_sampler=PathSampler(1.0),
        config=config,
        **GEN_KWARGS
    )
    gcode_service = GCodeGenerationService(gen)
    gcode = gcode_service.generate(points, {})
    g1_lines = [l for l in gcode if l.startswith('G1')]
    # Solo debe haber dos movimientos G1 (de 1,1 a 5,1 y de 5,1 a 9,1)
    assert len(g1_lines) >= 2, f"Se esperaba al menos 2 comandos G1, se encontraron: {g1_lines}"
