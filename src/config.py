"""
Path: src/config.py
"""

from pathlib import Path

# Rutas principales
SVG_INPUT_DIR = Path("svg_input")
GCODE_OUTPUT_DIR = Path("gcode_output")
LOGS_DIR = Path("logs")

# Parámetros de G-code
FEED = 400            # mm/min
CMD_DOWN = "M3 S50"   # baja herramienta / prende láser
CMD_UP = "M5"         # levanta herramienta / apaga láser
STEP_MM = 0.3         # resolución de muestreo sobre cada segmento
DWELL_MS = 150        # pausa (ms) tras subir/bajar herramienta
MAX_HEIGHT_MM = 250   # altura máxima permitida en mm
DWELL_MS = 150        # pausa (ms) tras subir/bajar herramienta
MAX_HEIGHT_MM = 250   # altura máxima permitida en mm
