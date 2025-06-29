from pathlib import Path
from typing import Optional, List
from domain.ports.file_selector_port import FileSelectorPort

class GcodeFileSelectorAdapter(FileSelectorPort):
    """Adaptador para selección de archivos GCODE desde la consola."""
    def __init__(self, config_provider=None, i18n=None, logger=None):
        self.config_provider = config_provider
        self.i18n = i18n
        self.logger = logger

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        # Stub para cumplir con la interfaz, no se usa en este adaptador
        return None

    def select_gcode_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite al usuario seleccionar un archivo GCODE desde la consola.
        """
        config = self._load_config()
        gcode_dir = initial_dir or config.get('GCODE_OUTPUT_DIR', './data/gcode_output')
        while True:
            gcode_files = self._find_gcode_files_recursively(gcode_dir)
            if gcode_files:
                self.logger.info(self.i18n.get("INFO_GCODE_FILES_FOUND"))
                for idx, file in enumerate(gcode_files, 1):
                    self.logger.option(f"  [{idx}] {file}")
                self.logger.option(self.i18n.get("OPTION_CANCEL"))
                try:
                    choice = int(input("[INPUT] " + self.i18n.get("PROMPT_SELECT_GCODE_FILE")))
                    if choice == 0:
                        self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED"))
                        return None
                    if 1 <= choice <= len(gcode_files):
                        return gcode_files[choice - 1]
                    self.logger.warning(self.i18n.get("WARN_INVALID_OPTION"))
                except ValueError:
                    self.logger.warning(self.i18n.get("WARN_INVALID_NUMBER"))
                except KeyboardInterrupt:
                    self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED_CTRL_C"))
                    return None
            else:
                self.logger.warning(self.i18n.get("WARN_NO_GCODE_FOUND", gcode_dir=gcode_dir))
                new_dir = input(self.i18n.get("PROMPT_NEW_GCODE_DIR"))
                if new_dir.lower() == 'q':
                    return None
                gcode_dir = new_dir

    def _find_gcode_files_recursively(self, directory: str) -> List[str]:
        path = Path(directory)
        if not path.exists():
            return []
        result = []
        for item in path.glob('**/*.gcode'):
            if item.is_file():
                result.append(str(item))
        return sorted(result)

    def _load_config(self):
        if self.config_provider:
            return self.config_provider
        return {}
