"""
Servicio de generación de nombres de archivos G-code únicos a partir de un archivo SVG.
"""
from pathlib import Path
from domain.ports.config_provider import ConfigProviderPort

class FilenameService:
    """
    Servicio de aplicación para generar nombres de archivos G-code únicos.
    """
    def __init__(self, config_provider: ConfigProviderPort):
        self.config_provider = config_provider

    def next_filename(self, svg_file: Path) -> Path:
        output_dir = self.config_provider.get_gcode_output_dir()
        stem = svg_file.stem
        for i in range(100):
            candidate = output_dir / f"{stem}_v{i:02d}.gcode"
            if not candidate.exists():
                return candidate
        raise RuntimeError("Too many output files for this SVG.")
