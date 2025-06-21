"""
GcodeFilenameGenerator: Clase para generar nombres de archivos de salida G-code únicos.
"""
from pathlib import Path

class GcodeFilenameGenerator:
    " Generador de nombres de archivos G-code a partir de un archivo SVG. "
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def next_filename(self, svg_file: Path) -> Path:
        " Genera un nombre de archivo G-code único basado en el nombre del SVG. "
        stem = svg_file.stem
        for i in range(100):
            candidate = self.output_dir / f"{stem}_v{i:02d}.gcode"
            if not candidate.exists():
                return candidate
        raise RuntimeError("Too many output files for this SVG.")
