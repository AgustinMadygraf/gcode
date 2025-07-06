"""
Adaptador: toma la lógica de dominio y la convierte en G-code final usando la configuración activa.
"""
from infrastructure.config.config import Config
from domain.gcode.reference_mark import reference_mark_gcode



class ReferenceMarksGenerator:
    """
    Clase adaptador para la generación de G-code de marcas de referencia.
    
    - Utiliza la configuración activa para determinar parámetros como feed, comandos de bajada/subida, dwell y área de trabajo.
    - Genera marcas en las cuatro esquinas del área definida (bottomleft, bottomright, topleft, topright).
    - Si la opción GENERATE_REFERENCE_MARKS está en False, omite los comandos de bajada/subida de herramienta, pero mantiene los movimientos.
    - Permite instrumentación con logger para depuración y trazabilidad del proceso.
    - Añade comentarios delimitadores en el G-code para identificar el bloque de marcas de referencia.
    """
    @staticmethod
    def generate(logger=None, width=None, height=None):
        """
        Genera el bloque de G-code correspondiente a las marcas de referencia.
        - Lee parámetros de configuración relevantes.
        - Genera marcas en las cuatro esquinas del área de trabajo.
        - Si GENERATE_REFERENCE_MARKS es False, omite comandos de bajada/subida de herramienta.
        - Permite logging detallado del proceso.
        """
        config = Config()
        feed = config.get("FEED", 4000)
        cmd_down = config.get("CMD_DOWN", "M3 S255")
        cmd_up = config.get("CMD_UP", "M5")
        dwell = config.get("DWELL_MS", 350)
        # Permite sobreescribir el área desde el adaptador principal para garantizar coherencia
        if width is not None and height is not None:
            area = [width, height]
        else:
            area = config.get("TARGET_WRITE_AREA_MM", [210.0, 148.0])
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
        if logger:
            logger.info(f"[REF_MARKS] Inicio generación de marcas de referencia. GENERATE_REFERENCE_MARKS={enable_marks}")
        body = []
        for x, y, direction in marks:
            if logger:
                logger.debug(f"[REF_MARKS] Generando marca en ({x}, {y}) dirección {direction}")
            for line in reference_mark_gcode(x, y, direction, feed):
                # CMD_DOWN/CMD_UP controlan la bajada/subida de herramienta
                if line == "CMD_DOWN":
                    if enable_marks:
                        body.append(cmd_down)
                        if logger:
                            logger.debug(f"[REF_MARKS] CMD_DOWN insertado en ({x}, {y})")
                    else:
                        if logger:
                            logger.debug(f"[REF_MARKS] CMD_DOWN omitido por configuración en ({x}, {y})")
                elif line == "CMD_UP":
                    if enable_marks:
                        body.append(cmd_up)
                        if logger:
                            logger.debug(f"[REF_MARKS] CMD_UP insertado en ({x}, {y})")
                    else:
                        if logger:
                            logger.debug(f"[REF_MARKS] CMD_UP omitido por configuración en ({x}, {y})")
                elif line == "DWELL":
                    # Pausa opcional para asegurar la marca
                    body.append(f"G4 P{dwell/1000}")
                else:
                    # Comando G-code estándar generado por la lógica de dominio
                    body.append(line)
        # Retorno al origen tras finalizar las marcas
        body.append("G0 X0 Y0")
        # --- Logging de finalización ---
        if logger:
            logger.info(f"[REF_MARKS] Finalización de la generación de marcas de referencia. Total líneas: {len(header) + len(body)}")
        # Comentario delimitador de fin de bloque
        body.append("; --- END OF AUTOMATIC REFERENCE MARKS ---")
        return "\n".join(header + body)
