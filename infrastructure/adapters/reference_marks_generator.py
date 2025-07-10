"""
Path: infrastructure/adapters/reference_marks_generator.py
Genera bloques de G-code para marcas de referencia y áreas en el área de trabajo.
Incluye marcas de referencia en las esquinas del área de trabajo y marcas para áreas específicas.
"""

from infrastructure.config.config import Config
from domain.gcode.reference_mark import reference_mark_gcode


# --- SRP/POO Refactor ---
class ReferenceMarkGenerator:
    "Genera el G-code para una marca de referencia en una posición específica."
    DEBUG_ENABLED = False

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def __init__(self, feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.dwell = dwell
        self.logger = logger
        self.i18n = i18n
        self.enable_marks = enable_marks

    def generate(self, x, y, direction):
        """
        Genera el G-code para una marca de referencia en (x, y) con dirección dada.
        """
        body = []
        for line in reference_mark_gcode(x, y, direction, self.feed):
            if line == "CMD_DOWN":
                if self.enable_marks:
                    body.append(self.cmd_down)
                    self._debug(f"[REF_MARKS] CMD_DOWN insertado en ({x}, {y})")
                else:
                    self._debug(f"[REF_MARKS] CMD_DOWN omitido por configuración en ({x}, {y})")
            elif line == "CMD_UP":
                if self.enable_marks:
                    body.append(self.cmd_up)
                    self._debug(f"[REF_MARKS] CMD_UP insertado en ({x}, {y})")
                else:
                    self._debug(f"[REF_MARKS] CMD_UP omitido por configuración en ({x}, {y})")
            elif line == "DWELL":
                body.append(f"G4 P{self.dwell/1000}")
            else:
                body.append(line)
        return body

class ReferenceMarkBlockGenerator:
    """
    Genera solo la primera marca de referencia (abajo izquierda) y su G-code.
    """
    def __init__(self, feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True):
        self.mark_generator = ReferenceMarkGenerator(feed, cmd_down, cmd_up, dwell, logger, i18n, enable_marks)
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.dwell = dwell
        self.logger = logger
        self.i18n = i18n
        self.enable_marks = enable_marks

    def generate(self, width, height):
        " Genera el bloque de G-code para las marcas de referencia."
        config = Config()
        target_area = config.get("TARGET_WRITE_AREA_MM", [width, height])
        target_x, target_y = target_area[0], target_area[1]
        marks = [
            (0, 0, 'bottomleft'),           # 1ra marca
            (target_x, 0, 'bottomright'),   # 2da marca
            (target_x, target_y, 'topright'), # 3ra marca
            (0, target_y, 'topleft')        # 4ta marca
        ]
        body = []
        for idx, (x, y, direction) in enumerate(marks):
            body.append(f"; Iniciando {idx+1}ra marca de referencia")
            body.append(f"G0 X{x} Y{y}")
            body.extend(self.mark_generator.generate(x, y, direction))
            body.append(f"G0 X{x} Y{y}")

        return body

class ReferenceMarksGenerator:
    " Generador de marcas de referencia para G-code."
    def __init__(self, logger=None, i18n=None, config=None):
        " Inicializa el generador de marcas de referencia."
        self.logger = logger
        self.i18n = i18n
        self.config = config

    def _debug(self, msg, *args, **kwargs):
        """
        Muestra mensajes de debug solo si el flag 'ReferenceMarkGenerator' está activado en la configuración.
        """
        debug_enabled = False
        if self.config and hasattr(self.config, "get_debug_flag"):
            debug_enabled = self.config.get_debug_flag("ReferenceMarkGenerator")
        if debug_enabled and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def generate(self, width=None, height=None):
        " Genera el bloque de G-code para las marcas de referencia y áreas."
        config = Config()
        feed = config.get("FEED")
        cmd_down = config.get("CMD_DOWN")
        cmd_up = config.get("CMD_UP")
        dwell = config.get("DWELL_MS")
        enable_marks = config.get("GENERATE_REFERENCE_MARKS", True)
        if width is not None and height is not None:
            area = [width, height]
        else:
            area = config.get("TARGET_WRITE_AREA_MM")
        width, height = area
        header = [
            "; --- START OF AUTOMATIC REFERENCE MARKS ---",
            "; Automatic reference marks",
            "G21",
            "G90"
        ]
        if enable_marks:
            header.append(cmd_up)
        self._debug(self.i18n.get("REF_MARKS_START", "[REF_MARKS] Inicio generación de marcas de referencia. GENERATE_REFERENCE_MARKS={}").format(enable_marks))
        self._debug(f"[REF_MARKS] Inicio generación de marcas de referencia. GENERATE_REFERENCE_MARKS={enable_marks}")
        body = []
        # Marcas de referencia principales
        ref_block = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, self.logger, self.i18n, enable_marks)
        body.extend(ref_block.generate(width, height))
        # Marcas de área
        body.append("G0 X0 Y0")
        body.append("; --- END OF AUTOMATIC REFERENCE MARKS ---")
        return "\n".join(header + body)
