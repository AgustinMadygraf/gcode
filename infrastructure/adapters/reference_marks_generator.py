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
        - Agrega marcas de las cuatro esquinas de PLOTTER_MAX_AREA_MM y TARGET_WRITE_AREA_MM.
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
        # Orden: abajo izquierda, abajo derecha, arriba derecha, arriba izquierda
        marks = [
            (0, 0, 'bottomleft'),
            (width, 0, 'bottomright'),
            (width, height, 'topright'),
            (0, height, 'topleft')
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

        # --- Marcas de PLOTTER_MAX_AREA_MM y TARGET_WRITE_AREA_MM ---
        def area_marks(area_name, area_xy):
            wx, hy = area_xy
            corners = [
                (0, 0, 'abajo izquierda'),
                (wx, 0, 'abajo derecha'),
                (wx, hy, 'arriba derecha'),
                (0, hy, 'arriba izquierda')
            ]
            for x, y, label in corners:
                body.append(f"; Marca {area_name} esquina {label}")
                body.append(f"G0 X{x} Y{y}")
                body.append(cmd_up)

        plotter_area = config.get("PLOTTER_MAX_AREA_MM")
        target_area = config.get("TARGET_WRITE_AREA_MM")
        if plotter_area:
            area_marks("PLOTTER_MAX_AREA_MM", plotter_area)
        if target_area:
            area_marks("TARGET_WRITE_AREA_MM", target_area)
        body.append("G0 X0 Y0")
        if self.logger and self.i18n:
            self.logger.info(self.i18n.get("REF_MARKS_END", "[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {}"
                ).format(len(header) + len(body)))
        elif self.logger:
            self.logger.info(f"[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {len(header) + len(body)}")
        body.append("; --- END OF AUTOMATIC REFERENCE MARKS ---")
        return "\n".join(header + body)
