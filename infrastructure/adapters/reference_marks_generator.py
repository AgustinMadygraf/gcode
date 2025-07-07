"""
Adaptador: toma la lógica de dominio y la convierte en G-code final usando la configuración activa.
"""
from infrastructure.config.config import Config
from domain.gcode.reference_mark import reference_mark_gcode



class ReferenceMarksGenerator:
    """
    Clase adaptador para la generación de G-code de marcas de referencia.
    """
    DEBUG_ENABLED = False

    def __init__(self, logger=None, i18n=None):
        """
        Inicializa el generador de marcas de referencia con logger e i18n opcionales.
        """
        self.logger = logger
        self.i18n = i18n

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def generate(self, width=None, height=None):
        """
        Genera el bloque de G-code correspondiente a las marcas de referencia.
        - Lee parámetros de configuración relevantes.
        - Genera marcas en las cuatro esquinas del área de trabajo.
        - Si GENERATE_REFERENCE_MARKS es False, omite comandos de bajada/subida de herramienta.
        - Permite logging detallado del proceso.
        - Usa self.logger y self.i18n para mensajes localizados.
        """
        config = Config()
        feed = config.get("FEED")
        cmd_down = config.get("CMD_DOWN")
        cmd_up = config.get("CMD_UP")
        dwell = config.get("DWELL_MS")
        # Permite sobreescribir el área desde el adaptador principal para garantizar coherencia
        if width is not None and height is not None:
            area = [width, height]
        else:
            area = config.get("TARGET_WRITE_AREA_MM")
        width, height = area
        marks = [
            (0, 0, 'bottomleft'),
            (width, 0, 'bottomright'),
            (0, height, 'topleft'),
            (width, height, 'topright')
        ]
        # Leer la opción de marcas de referencia
        enable_marks = config.get("GENERATE_REFERENCE_MARKS", True)
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
        for x, y, direction in marks:
            self._debug(f"[REF_MARKS] Generando marca en ({x}, {y}) dirección {direction}")
            for line in reference_mark_gcode(x, y, direction, feed):
                if line == "CMD_DOWN":
                    if enable_marks:
                        body.append(cmd_down)
                        self._debug(f"[REF_MARKS] CMD_DOWN insertado en ({x}, {y})")
                    else:
                        self._debug(f"[REF_MARKS] CMD_DOWN omitido por configuración en ({x}, {y})")
                elif line == "CMD_UP":
                    if enable_marks:
                        body.append(cmd_up)
                        self._debug(f"[REF_MARKS] CMD_UP insertado en ({x}, {y})")
                    else:
                        self._debug(f"[REF_MARKS] CMD_UP omitido por configuración en ({x}, {y})")
                elif line == "DWELL":
                    body.append(f"G4 P{dwell/1000}")
                else:
                    body.append(line)
        body.append("G0 X0 Y0")
        if self.logger and self.i18n:
            self.logger.info(self.i18n.get("REF_MARKS_END", "[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {}"
                ).format(len(header) + len(body)))
        elif self.logger:
            self.logger.info(f"[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {len(header) + len(body)}")
        body.append("; --- END OF AUTOMATIC REFERENCE MARKS ---")
        return "\n".join(header + body)
