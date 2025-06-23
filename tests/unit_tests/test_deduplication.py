import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from infrastructure.svg_loader import SvgLoaderAdapter
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.entities.point import Point
from infrastructure.optimizers.optimization_chain import OptimizationChain
from infrastructure.path_sampler import PathSampler

SVG_SIMPLE_LINE = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M1 1 L9 1"/></svg>'''
SVG_BROKEN_LINE = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M1 1 L5 1 M5.001 1 L9 1"/></svg>'''

# Parámetros mínimos para GCodeGenerator
GEN_KWARGS = dict(feed=1000, cmd_down="M3 S255", cmd_up="M5", step_mm=1.0, dwell_ms=0, max_height_mm=10, optimizer=OptimizationChain())

def test_single_line_no_duplicate_g1(tmp_path):
    # Guardar SVG temporal
    svg_path = tmp_path / "line.svg"
    svg_path.write_text(SVG_SIMPLE_LINE)
    loader = SvgLoaderAdapter(str(svg_path))
    subpaths = loader.get_subpaths()
    # Simular muestreo de puntos (sin interpolación)
    points = [[Point(seg.start.real, seg.start.imag), Point(seg.end.real, seg.end.imag)] for p in subpaths for seg in p]
    generator = GCodeGeneratorAdapter(
        path_sampler=PathSampler(1.0),
        **GEN_KWARGS
    )
    gcode_service = GCodeGenerationService(generator)
    gcode = gcode_service.generate_gcode_commands(points)
    # Debe haber solo un bloque de G1 para la línea
    g1_lines = [l for l in gcode if l.startswith('G1')]
    assert len(g1_lines) == 1, f"Se esperaban 1 comando G1, se encontraron: {g1_lines}"
    # No debe haber doble trazo
    assert gcode.count('M3 S255') == 1, "Debe haber un solo comando de bajada de herramienta"
    assert gcode.count('M5') == 1, "Debe haber un solo comando de elevación de herramienta"

def test_broken_line_creates_two_traces(tmp_path):
    svg_path = tmp_path / "broken.svg"
    svg_path.write_text(SVG_BROKEN_LINE)
    loader = SvgLoaderAdapter(str(svg_path))
    subpaths = loader.get_subpaths()
    points = [[Point(seg.start.real, seg.start.imag), Point(seg.end.real, seg.end.imag)] for p in subpaths for seg in p]
    gen = GCodeGeneratorAdapter(path_sampler=PathSampler(1.0), **GEN_KWARGS)
    gcode_service = GCodeGenerationService(gen)
    gcode = gcode_service.generate_gcode_commands(points)
    # Debe haber dos bloques de G1
    g1_lines = [l for l in gcode if l.startswith('G1')]
    assert len(g1_lines) == 2, f"Se esperaban 2 comandos G1, se encontraron: {g1_lines}"
    assert gcode.count('M3 S255') == 2, "Debe haber dos comandos de bajada de herramienta"
    assert gcode.count('M5') == 2, "Debe haber dos comandos de elevación de herramienta"

def test_no_duplicate_points():
    # Simula puntos duplicados
    points = [[Point(1, 1), Point(1, 1), Point(5, 1), Point(9, 1), Point(9, 1)]]
    gen = GCodeGeneratorAdapter(
        path_sampler=PathSampler(1.0),
        **GEN_KWARGS
    )
    gcode_service = GCodeGenerationService(gen)
    gcode = gcode_service.generate_gcode_commands(points)
    g1_lines = [l for l in gcode if l.startswith('G1')]
    # Solo debe haber dos movimientos G1 (de 1,1 a 5,1 y de 5,1 a 9,1)
    assert len(g1_lines) == 2, f"Se esperaban 2 comandos G1, se encontraron: {g1_lines}"
