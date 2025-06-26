"""
GCodeValidator: Valida la integridad básica de archivos G-code.
"""
import re

class GCodeValidator:
    @staticmethod
    def validate(gcode_lines):
        """
        Valida una lista de líneas de G-code.
        Retorna (True, None) si es válido, (False, mensaje_error) si no.
        """
        if not gcode_lines:
            return False, "El archivo G-code está vacío."
        
        # Patrón extendido para comandos G-code estándar y comentarios (; o entre paréntesis)
        gcode_pattern = re.compile(r"^(G0|G1|G2|G3|G4|G20|G21|G28|G90|G91|G92|M\d+|;|\s|\(.*\)|$)", re.IGNORECASE)
        for idx, line in enumerate(gcode_lines, 1):
            if not gcode_pattern.match(line.strip()):
                return False, f"Línea {idx}: Comando G-code no reconocido: '{line.strip()}'"
        return True, None
