"""
SvgFileSelector: Clase para selección de archivos SVG desde un directorio.
"""
from pathlib import Path
from typing import Optional, List
from cli.i18n import MESSAGES
from infrastructure.i18n.i18n_service import I18nService

i18n = I18nService(MESSAGES)

class SvgFileSelector:
    " Clase para selección de archivos SVG desde un directorio. "
    def __init__(self, svg_dir: Path):
        self.svg_dir = svg_dir

    def list_svg_files(self) -> List[Path]:
        " Lista todos los archivos SVG en el directorio especificado. "
        return sorted(self.svg_dir.glob("*.svg"))

    def select(self, prompt: Optional[str] = None) -> Path:
        " Permite al usuario seleccionar un archivo SVG de una lista. "
        svg_files = self.list_svg_files()
        if not svg_files:
            raise FileNotFoundError("No SVG files found in svg_input.")
        print(i18n.get("available_svg_files"))
        for idx, f in enumerate(svg_files, 1):
            print(f"  {idx}. {f.name}")
        while True:
            try:
                sel = int(input(prompt or f"Select an SVG file (1-{len(svg_files)}): "))
                if 1 <= sel <= len(svg_files):
                    return svg_files[sel-1]
            except (ValueError, TypeError):
                pass
            print(i18n.get("invalid_selection"))
