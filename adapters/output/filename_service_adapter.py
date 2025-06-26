"""
Implementación del adaptador FilenameService.
Este adaptador maneja los detalles técnicos de generación de nombres de archivo,
que son detalles de infraestructura y no reglas de negocio.
"""
from pathlib import Path
import re
from domain.ports.filename_service_port import FilenameServicePort

class FilenameServiceAdapter(FilenameServicePort):
    """
    Adaptador que implementa la lógica de generación de nombres de archivos.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def next_filename(self, source_file: Path) -> Path:
        self.output_dir.mkdir(exist_ok=True, parents=True)
        base_name = source_file.stem
        pattern = re.compile(f"^{re.escape(base_name)}_v(\\d+)\\.gcode$")
        max_version = -1
        for existing_file in self.output_dir.glob(f"{base_name}_v*.gcode"):
            match = pattern.match(existing_file.name)
            if match:
                version = int(match.group(1))
                max_version = max(max_version, version)
        next_version = max_version + 1
        return self.output_dir / f"{base_name}_v{next_version:02d}.gcode"
