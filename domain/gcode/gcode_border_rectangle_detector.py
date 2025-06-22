class GCodeBorderRectangleDetector:
    """Detecta el rectángulo-borde al inicio del G-code."""
    def __init__(self, max_position=15, min_g1=4):
        self.max_position = max_position
        self.min_g1 = min_g1

    def detect_border_pattern(self, gcode_lines):
        """
        Retorna los índices de las líneas que conforman el rectángulo-borde o None si no se detecta.
        Detecta un bloque inicial con:
        - G0 (inicio)
        - G4 (pausa)
        - G0 (mover a esquina opuesta)
        - G4 (pausa)
        - M3 (bajar lapicera)
        - G4 (pausa)
        - >=4 líneas G1 (trazando rectángulo)
        - G4 (pausa)
        - M5 (subir lapicera)
        - G4 (pausa)
        """
        lines = gcode_lines[:self.max_position]
        if len(lines) < 10:
            return None
        # Buscar secuencia: G0, G4, G0, G4, M3, G4, >=4xG1, G4, M5, G4
        idx = 0
        if not lines[idx].startswith("G0 "):
            return None
        idx += 1
        if not lines[idx].startswith("G4 "):
            return None
        idx += 1
        if not lines[idx].startswith("G0 "):
            return None
        idx += 1
        if not lines[idx].startswith("G4 "):
            return None
        idx += 1
        if not lines[idx].startswith("M3"):
            return None
        idx += 1
        if not lines[idx].startswith("G4 "):
            return None
        idx += 1
        g1_start = idx
        g1_count = 0
        while idx < len(lines) and lines[idx].startswith("G1 "):
            g1_count += 1
            idx += 1
        if g1_count < self.min_g1:
            return None
        if idx >= len(lines) or not lines[idx].startswith("G4 "):
            return None
        idx += 1
        if idx >= len(lines) or not lines[idx].startswith("M5"):
            return None
        idx += 1
        # Opcional: G4 tras M5
        if idx < len(lines) and lines[idx].startswith("G4 "):
            idx += 1
        # Retornar los índices del bloque detectado
        return list(range(idx))
