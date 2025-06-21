"""
SvgFileSelector: Clase para selección de archivos SVG desde un directorio.
"""
from pathlib import Path
from typing import Optional, List

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
        print("Available SVG files:")
        for idx, f in enumerate(svg_files, 1):
            print(f"  {idx}. {f.name}")
        while True:
            try:
                sel = int(input(prompt or f"Select an SVG file (1-{len(svg_files)}): "))
                if 1 <= sel <= len(svg_files):
                    return svg_files[sel-1]
            except (ValueError, TypeError):
                pass
            print("Invalid selection. Try again.")
