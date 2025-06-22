"""
Config loader: Loads configuration from config.json, with defaults.
"""

import json
from pathlib import Path

# Valores por defecto
_DEFAULTS = {
    "SVG_INPUT_DIR": "svg_input",
    "GCODE_OUTPUT_DIR": "gcode_output",
    "FEED": 4000,
    "CMD_DOWN": "M3 S255; baja lapicera",
    "CMD_UP": "M5; sube lapicera",
    "STEP_MM": 0.3,
    "DWELL_MS": 350,
    "MAX_HEIGHT_MM": 250,
    "REMOVE_SVG_BORDER": True,
    "BORDER_DETECTION_TOLERANCE": 0.05
}

class Config:
    " Clase para cargar la configuración desde un archivo JSON. "
    def __init__(self, config_path: Path = Path(__file__).parent / "config.json"):
        self._data = _DEFAULTS.copy()
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    user_data = json.load(f)
                self._data.update(user_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Config] Error loading config.json: {e}. Using defaults.")

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        " Devuelve el valor de la clave, o un valor por defecto si no existe. "
        return self._data.get(key, default)

    @property
    def svg_input_dir(self):
        " Devuelve el directorio de entrada de SVG como un objeto Path. "
        return Path(self._data["SVG_INPUT_DIR"])

    @property
    def gcode_output_dir(self):
        " Devuelve el directorio de salida de GCODE como un objeto Path. "
        return Path(self._data["GCODE_OUTPUT_DIR"])

    @property
    def feed(self):
        " Devuelve la velocidad de alimentación (FEED) en mm/min. "
        return self._data["FEED"]

    @property
    def cmd_down(self):
        " Devuelve el comando para bajar el cabezal. "
        return self._data["CMD_DOWN"]

    @property
    def cmd_up(self):
        " Devuelve el comando para subir el cabezal. "
        return self._data["CMD_UP"]

    @property
    def step_mm(self):
        " Devuelve el paso (STEP_MM) en mm. "
        return self._data["STEP_MM"]

    @property
    def dwell_ms(self):
        " Devuelve el tiempo de espera (DWELL_MS) en ms. "
        return self._data["DWELL_MS"]

    @property
    def max_height_mm(self):
        " Devuelve la altura máxima (MAX_HEIGHT_MM) en mm. "
        return self._data["MAX_HEIGHT_MM"]

    @property
    def remove_svg_border(self):
        " Devuelve si se debe eliminar el borde del SVG. "
        return self._data.get("REMOVE_SVG_BORDER", True)

    @property
    def border_detection_tolerance(self):
        " Devuelve la tolerancia para detección de bordes SVG. "
        return self._data.get("BORDER_DETECTION_TOLERANCE", 0.05)

# Instancia global (Singleton)
_config = Config()

# Exportar variables para compatibilidad
SVG_INPUT_DIR = _config.svg_input_dir
GCODE_OUTPUT_DIR = _config.gcode_output_dir
FEED = _config.feed
CMD_DOWN = _config.cmd_down
CMD_UP = _config.cmd_up
STEP_MM = _config.step_mm
DWELL_MS = _config.dwell_ms
MAX_HEIGHT_MM = _config.max_height_mm
REMOVE_SVG_BORDER = _config.remove_svg_border
BORDER_DETECTION_TOLERANCE = _config.border_detection_tolerance
