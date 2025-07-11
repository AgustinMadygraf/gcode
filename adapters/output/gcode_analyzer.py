"""
Path: adapters/output/gcode_analyzer.py
"""

import re

class GCodeAnalyzer:
    " Clase para analizar G-code y extraer información relevante. "
    @staticmethod
    def get_width_from_gcode_lines(gcode_lines):
        " Extrae el ancho del G-code a partir de las coordenadas X. "
        x_values = []
        for line in gcode_lines:
            match = re.search(r'[Gg][01]\s+X([-+]?\d*\.?\d+)', line)
            if match:
                x_values.append(float(match.group(1)))
        if not x_values:
            return 0.0
        return max(x_values) - min(x_values)
