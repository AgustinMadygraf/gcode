"""
SvgFileSelector: Clase para selección de archivos SVG desde un directorio.
"""
from pathlib import Path
from typing import Optional, List
from cli.i18n import MESSAGES
from infrastructure.i18n.i18n_service import I18nService


i18n = I18nService(MESSAGES)

class SvgFileSelector:
    """Clase para selección de archivos SVG desde un directorio."""
    def __init__(self, svg_dir: Path, logger):
        self.svg_dir = svg_dir
        self.logger = logger

    def list_svg_files(self) -> List[Path]:
        """Lista todos los archivos SVG en el directorio especificado."""
        return sorted(self.svg_dir.glob("*.svg"))

    def select(self, prompt: Optional[str] = None) -> Path:
        """Permite al usuario seleccionar un archivo SVG de una lista."""
        svg_files = self.list_svg_files()
        if not svg_files:
            raise FileNotFoundError(i18n.get("WARN_NO_SVG_FOUND", svg_input_dir=str(self.svg_dir)))
        self.logger.info(i18n.get("INFO_SVG_FILES_FOUND"))
        for idx, f in enumerate(svg_files, 1):
            self.logger.info(i18n.get("OPTION_SVG_FILE", num=idx, filename=f.name))
        while True:
            try:
                sel = int(input(prompt or i18n.get("PROMPT_SELECT_SVG_FILE_RANGE", range=f"1-{len(svg_files)}")))
                if 1 <= sel <= len(svg_files):
                    return svg_files[sel-1]
            except (ValueError, TypeError):
                pass
            self.logger.warning(i18n.get("ERROR_INVALID_SELECTION"))
