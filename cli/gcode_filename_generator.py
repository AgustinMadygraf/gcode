"""
GcodeFilenameGenerator: Clase para generar nombres de archivos de salida G-code únicos.
Ahora delega la lógica al servicio de aplicación FilenameService.
"""
from pathlib import Path
from application.use_cases.file_output.filename_service import FilenameService

class GcodeFilenameGenerator:
    """
    Generador de nombres de archivos G-code a partir de un archivo SVG.
    Ahora delega la lógica al servicio de aplicación FilenameService.
    """
    def __init__(self, output_dir: Path):
        self._service = FilenameService(output_dir)

    def next_filename(self, svg_file: Path) -> Path:
        return self._service.next_filename(svg_file)
