"""
settings.py: Configuraciones técnicas de infraestructura
"""
import json
import shutil
from pathlib import Path

class InfraSettings:
    def __init__(self, config_path: Path):
        # Si no existe config.json, intenta copiar desde config_default.json
        if not config_path.exists():
            default_config_path = config_path.parent / "config_default.json"
            if default_config_path.exists():
                shutil.copy(default_config_path, config_path)
            else:
                raise FileNotFoundError(
                    f"No se encontró ni {config_path} ni {default_config_path}"
                )
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)
        data = self.config
        self._svg_input_dir = Path(data["SVG_INPUT_DIR"])
        self._gcode_output_dir = Path(data["GCODE_OUTPUT_DIR"])
        self._cmd_down = data["CMD_DOWN"]
        self._cmd_up = data["CMD_UP"]
        self._remove_svg_border = data.get("REMOVE_BORDER_RECTANGLE", True)
        self._feed = data.get("FEED", 4000)
        self._step_mm = data.get("STEP_MM", 0.3)
        self._dwell_ms = data.get("DWELL_MS", 350)
        self._max_height_mm = data.get("MAX_HEIGHT_MM", 250)
        self._border_detection_tolerance = data.get("BORDER_DETECTION_TOLERANCE", 0.05)

    def get_svg_input_dir(self) -> Path:
        return self._svg_input_dir

    def get_gcode_output_dir(self) -> Path:
        return self._gcode_output_dir

    def get_cmd_down(self) -> str:
        return self._cmd_down

    def get_cmd_up(self) -> str:
        return self._cmd_up

    def get_remove_svg_border(self) -> bool:
        return self._remove_svg_border

    def get_feed(self) -> int:
        return self._feed

    def get_step_mm(self) -> float:
        return self._step_mm

    def get_dwell_ms(self) -> int:
        return self._dwell_ms

    def get_max_height_mm(self) -> int:
        return self._max_height_mm

    def get_border_detection_tolerance(self) -> float:
        return self._border_detection_tolerance

    def as_dict(self):
        return {
            "SVG_INPUT_DIR": str(self._svg_input_dir),
            "GCODE_OUTPUT_DIR": str(self._gcode_output_dir),
            "CMD_DOWN": self._cmd_down,
            "CMD_UP": self._cmd_up,
            "REMOVE_BORDER_RECTANGLE": self._remove_svg_border,
            "FEED": self._feed,
            "STEP_MM": self._step_mm,
            "DWELL_MS": self._dwell_ms,
            "MAX_HEIGHT_MM": self._max_height_mm,
            "BORDER_DETECTION_TOLERANCE": self._border_detection_tolerance
        }

    def get(self, key, default=None):
        return self.config.get(key, default)
