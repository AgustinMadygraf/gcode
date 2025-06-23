"""
Config loader: Loads configuration from config.json, with defaults.
"""

import json
import shutil
from pathlib import Path

class Config:
    " Clase para cargar la configuración desde un archivo JSON. "
    def __init__(self, config_path: Path = Path(__file__).parent / "config.json"):
        default_path = Path(__file__).parent / "config_default.json"
        # Si no existe config.json, crear uno a partir de config_default.json
        if not config_path.exists() and default_path.exists():
            try:
                shutil.copy(default_path, config_path)
            except (PermissionError, OSError) as e:
                print(f"[Config] Error copying default config: {e}. Using defaults.")
        self._data = {}
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    user_data = json.load(f)
                self._data.update(user_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Config] Error loading config.json: {e}. Using empty config.")

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
