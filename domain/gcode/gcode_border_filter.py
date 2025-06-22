class GCodeBorderFilter:
    """Filtra el rectángulo-borde del G-code generado."""
    def __init__(self, detector):
        self.detector = detector

    def filter(self, gcode_content):
        lines = gcode_content.split('\n')
        border_indices = self.detector.detect_border_pattern(lines)
        if border_indices:
            filtered = [l for i, l in enumerate(lines) if i not in border_indices]
            return '\n'.join(filtered)
        return gcode_content
