"""
Servicio de generación de nombres de archivos G-code únicos a partir de un archivo SVG.
"""
from pathlib import Path

class FilenameService:
    """
    Servicio de aplicación para generar nombres de archivos G-code únicos.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def next_filename(self, svg_file: Path) -> Path:
        stem = svg_file.stem
        for i in range(100):
            candidate = self.output_dir / f"{stem}_v{i:02d}.gcode"
            if not candidate.exists():
                return candidate
        raise RuntimeError("Too many output files for this SVG.")
