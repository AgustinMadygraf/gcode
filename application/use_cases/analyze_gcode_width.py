"""
Path: application/use_cases/analyze_gcode_width.py
"""

from adapters.output.gcode_analyzer import GCodeAnalyzer

def analyze_gcode_width(gcode_path):
    " Analiza el G-code y devuelve el ancho calculado. "
    with open(gcode_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return GCodeAnalyzer.get_width_from_gcode_lines(lines)
