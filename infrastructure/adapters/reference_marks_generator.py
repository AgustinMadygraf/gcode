"""
Path: infrastructure/adapters/reference_marks_generator.py
Genera bloques de G-code para marcas de referencia y áreas en el área de trabajo.
Incluye marcas de referencia en las esquinas del área de trabajo y marcas para áreas específicas.
"""

from infrastructure.config.config import Config
from domain.gcode.reference_mark import reference_mark_gcode

class ReferenceMarkBlockGenerator:
    " Genera el bloque de G-code para las marcas de referencia."
    def __init__(self, feed, cmd_down, cmd_up, dwell, logger=None, i18n=None, enable_marks=True):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.dwell = dwell
        self.logger = logger
        self.i18n = i18n
        self.enable_marks = enable_marks

    def _debug(self, msg):
        if self.logger:
            self.logger.debug(msg)

    def generate(self, width, height):
        """
        Genera el bloque de G-code para las marcas de referencia principales.
        """
        ref_points = [
            (0, 0, 'bottomleft'),
            (width, 0, 'bottomright'),
            (width, height, 'topright'),
            (0, height, 'topleft')
        ]
        body = []
        for idx, (x, y, direction) in enumerate(ref_points):
            self._debug(f"[REF_MARKS] Generando marca en ({x}, {y}) dirección {direction}")
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
            # Movimientos especiales en un solo eje tras cada marca de referencia
            if idx == 0:
                # Tras la primera marca: mover solo en Y al extremo inferior (Y=0)
                body.append(f"G0 X{x} Y0")
            elif idx == 1:
                # Tras la segunda marca: mover solo en X al extremo derecho (X=width)
                body.append(f"G0 X{width} Y{y}")
            elif idx == 2:
                # Tras la tercera marca: mover solo en Y al extremo superior (Y=height)
                body.append(f"G0 X{x} Y{height}")
            elif idx == 3:
                # Tras la cuarta marca: mover solo en X al extremo izquierdo (X=0)
                body.append(f"G0 X0 Y{y}")
        return body

class AreaMarkBlockGenerator:
    " Genera el bloque de G-code para las marcas de área."
    def __init__(self, cmd_up):
        self.cmd_up = cmd_up

    def generate(self, area_name, area_xy):
        " Genera el bloque de G-code para las marcas de un área específica."
        wx, hy = area_xy
        corners = [
            (0, 0, 'abajo izquierda'),
            (wx, 0, 'abajo derecha'),
            (wx, hy, 'arriba derecha'),
            (0, hy, 'arriba izquierda')
        ]
        body = []
        for x, y, label in corners:
            body.append(f"; Marca {area_name} esquina {label}")
            body.append(f"G0 X{x} Y{y}")
            body.append(self.cmd_up)
        return body


class ReferenceMarksGenerator:
    " Generador de marcas de referencia para G-code."
    DEBUG_ENABLED = False

    def __init__(self, logger=None, i18n=None):
        " Inicializa el generador de marcas de referencia."
        self.logger = logger
        self.i18n = i18n

    def _debug(self, msg, *args, **kwargs):
        " Registra un mensaje de depuración si el logger está configurado."
        if self.DEBUG_ENABLED and self.logger:
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
        if self.logger and self.i18n:
            self.logger.info(self.i18n.get("REF_MARKS_START", "[REF_MARKS] Inicio generación de marcas de referencia. GENERATE_REFERENCE_MARKS={}").format(enable_marks))
        elif self.logger:
            self.logger.info(f"[REF_MARKS] Inicio generación de marcas de referencia. GENERATE_REFERENCE_MARKS={enable_marks}")
        body = []
        # Marcas de referencia principales
        ref_block = ReferenceMarkBlockGenerator(feed, cmd_down, cmd_up, dwell, self.logger, self.i18n, enable_marks)
        body.extend(ref_block.generate(width, height))
        # Marcas de área
        area_block = AreaMarkBlockGenerator(cmd_up)
        plotter_area = config.get("PLOTTER_MAX_AREA_MM")
        target_area = config.get("TARGET_WRITE_AREA_MM")
        if plotter_area:
            body.extend(area_block.generate("PLOTTER_MAX_AREA_MM", plotter_area))
        if target_area:
            body.extend(area_block.generate("TARGET_WRITE_AREA_MM", target_area))
        body.append("G0 X0 Y0")
        if self.logger and self.i18n:
            self.logger.info(self.i18n.get("REF_MARKS_END", "[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {}"
                ).format(len(header) + len(body)))
        elif self.logger:
            self.logger.info(f"[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {len(header) + len(body)}")
        body.append("; --- END OF AUTOMATIC REFERENCE MARKS ---")
        return "\n".join(header + body)
