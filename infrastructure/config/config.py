"""
Config loader: Loads configuration from config.json, with defaults.
"""

import json
import shutil
from pathlib import Path

class Config:
    """
    Clase para cargar la configuración desde un archivo JSON.
    - Usa PLOTTER_MAX_AREA_MM para definir el área máxima de la plotter (ancho, alto).
    - El campo MAX_HEIGHT_MM está deprecado y no debe usarse.
    - Todos los métodos y validaciones usan la nueva convención.
    """
    @property
    def rotate_90_clockwise(self):
        """Devuelve si debe rotar 90 grados en sentido horario (ROTATE_90_CLOCKWISE)."""
        return bool(self._data.get("ROTATE_90_CLOCKWISE", False))

    def __init__(self, config_path: Path = Path(__file__).parent / "config.json"):
        default_path = Path(__file__).parent / "config_default.json"
        # Si no existe config.json, crear uno a partir de config_default.json
        if not config_path.exists() and default_path.exists():
            try:
                shutil.copy(default_path, config_path)
            except (PermissionError, OSError) as e:
                print(f"[Config] Error copying default config: {e}. Using defaults.")
        self._data = {}
        # Primero cargar los defaults
        if default_path.exists():
            try:
                with open(default_path, encoding="utf-8") as f:
                    defaults = json.load(f)
                self._data.update(defaults)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Config] Error loading config_default.json: {e}. Using empty defaults.")
        # Luego sobreescribir con el config del usuario si existe
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    user_data = json.load(f)
                self._data.update(user_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Config] Error loading config.json: {e}. Using defaults only.")
        # Validar TOOL_DIAMETER
        if "TOOL_DIAMETER" not in self._data or not isinstance(self._data["TOOL_DIAMETER"], (int, float)):
            self._data["TOOL_DIAMETER"] = 0.4
        self._validate_config()
    @property
    def tool_diameter(self):
        """Diámetro de la herramienta en mm (por defecto 0.4)"""
        return self._data.get("TOOL_DIAMETER", 0.4)

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
        "Devuelve el paso en mm (STEP_MM)."
        return self._data["STEP_MM"]

    @property
    def dwell_ms(self):
        "Devuelve el tiempo de espera en ms (DWELL_MS)."
        return self._data["DWELL_MS"]

    @property
    def remove_svg_border(self):
        "Devuelve si se debe eliminar el borde SVG (REMOVE_BORDER_RECTANGLE)."
        return self._data.get("REMOVE_BORDER_RECTANGLE", True)

    @property
    def border_detection_tolerance(self):
        "Devuelve la tolerancia para detección de borde (BORDER_DETECTION_TOLERANCE)."
        return self._data.get("BORDER_DETECTION_TOLERANCE", 0.05)

    @property
    def mirror_vertical(self):
        "Devuelve si se debe aplicar la inversión vertical (MIRROR_VERTICAL)."
        return self._data.get("MIRROR_VERTICAL", True)

    @property
    def curvature_adjustment_factor(self):
        """Factor de ajuste de velocidad en curvas (0.1-0.4, por defecto 0.25)"""
        return self._data.get("CURVATURE_ADJUSTMENT_FACTOR", 0.25)

    @property
    def minimum_feed_factor(self):
        """Factor mínimo de velocidad (0.0-1.0, por defecto 0.5)"""
        return self._data.get("MINIMUM_FEED_FACTOR", 0.5)

    @property
    def tool_type(self):
        """Tipo de herramienta seleccionada (pen o marker)"""
        return self._data.get("TOOL_TYPE", "pen")  # Default: lapicera

    @property
    def pen_double_pass(self):
        """Si es True, los trazos con lapicera se hacen dos veces (ida y vuelta)"""
        return self._data.get("PEN_DOUBLE_PASS", True)

    @property
    def marker_feed_rate(self):
        """Velocidad específica para fibrón (usualmente más lenta que lapicera)"""
        return self._data.get("MARKER_FEED_RATE", self.feed * 0.7)  # 70% de la velocidad normal

    @property
    def plotter_max_area_mm(self):
        """Devuelve el área máxima de la plotter [ancho_mm, alto_mm] como lista de dos floats."""
        return self._data.get("PLOTTER_MAX_AREA_MM", [300.0, 260.0])

    @property
    def target_write_area_mm(self):
        """Devuelve el área objetivo de escritura [ancho_mm, alto_mm] como lista de dos floats."""
        return self._data.get("TARGET_WRITE_AREA_MM", [297.0, 210.0])

    def get_gcode_output_dir(self):
        "Compatibilidad: Devuelve el directorio de salida de GCODE."
        return self.gcode_output_dir

    def get_remove_svg_border(self):
        "Compatibilidad: Devuelve si se debe eliminar el borde SVG."
        return self.remove_svg_border

    def get_border_detection_tolerance(self):
        "Compatibilidad: Devuelve la tolerancia para detección de borde."
        return self.border_detection_tolerance

    def get_mirror_vertical(self):
        "Compatibilidad: Devuelve si se debe aplicar la inversión vertical."
        return self.mirror_vertical

    def _validate_area(self, value, key, default):
        """Valida que value sea una lista de dos floats positivos. Si no, retorna default y loguea warning."""
        if not (isinstance(value, list) and len(value) == 2 and all(isinstance(x, (int, float)) and x > 0 for x in value)):
            print(f"[Config] Valor inválido para '{key}', usando valor por defecto: {default}")
            return default
        return value

    def _validate_config(self):
        """Valida y corrige los campos críticos de la configuración usando los valores por defecto si es necesario."""
        # Cargar defaults
        default_path = Path(__file__).parent / "config_default.json"
        with open(default_path, encoding="utf-8") as f:
            defaults = json.load(f)
        # Validar áreas
        self._data["PLOTTER_MAX_AREA_MM"] = self._validate_area(
            self._data.get("PLOTTER_MAX_AREA_MM", defaults["PLOTTER_MAX_AREA_MM"]),
            "PLOTTER_MAX_AREA_MM",
            defaults["PLOTTER_MAX_AREA_MM"]
        )
        self._data["TARGET_WRITE_AREA_MM"] = self._validate_area(
            self._data.get("TARGET_WRITE_AREA_MM", defaults["TARGET_WRITE_AREA_MM"]),
            "TARGET_WRITE_AREA_MM",
            defaults["TARGET_WRITE_AREA_MM"]
        )
        # El área objetivo no debe exceder el área máxima
        t = self._data["TARGET_WRITE_AREA_MM"]
        m = self._data["PLOTTER_MAX_AREA_MM"]
        if t[0] > m[0] or t[1] > m[1]:
            print(f"[Config] TARGET_WRITE_AREA_MM excede PLOTTER_MAX_AREA_MM, usando valor por defecto: {defaults['TARGET_WRITE_AREA_MM']}")
            self._data["TARGET_WRITE_AREA_MM"] = defaults["TARGET_WRITE_AREA_MM"]

    def get_debug_flag(self, name: str) -> bool:
        """
        Devuelve el flag de debug para un componente dado, según la sección DEBUG del config.
        Si no existe, retorna False por defecto.
        """
        debug_section = self._data.get("DEBUG", {})
        return bool(debug_section.get(name, False))
