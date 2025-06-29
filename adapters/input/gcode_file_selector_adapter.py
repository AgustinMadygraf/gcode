from pathlib import Path
from typing import Optional, List
from domain.ports.file_selector_port import FileSelectorPort
from infrastructure.logger import logger

class GcodeFileSelectorAdapter(FileSelectorPort):
    """Adaptador para selección de archivos GCODE desde la consola."""
    def __init__(self, config_provider=None):
        self.config_provider = config_provider

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
                logger.info("\nArchivos GCODE encontrados:")
                for idx, file in enumerate(gcode_files, 1):
                    logger.option(f"  [{idx}] {file}")
                logger.option("  [0] Cancelar")
                try:
                    choice = int(input("[INPUT] Seleccione un archivo GCODE por número: "))
                    if choice == 0:
                        logger.info("Operación cancelada por el usuario.")
                        return None
                    if 1 <= choice <= len(gcode_files):
                        return gcode_files[choice - 1]
                    logger.warning("Opción inválida.")
                except ValueError:
                    logger.warning("Por favor, ingrese un número válido.")
                except KeyboardInterrupt:
                    logger.info("\nOperación cancelada por el usuario (Ctrl+C).")
                    return None
            else:
                logger.warning(f"No se encontraron archivos GCODE en {gcode_dir}")
                new_dir = input("[INPUT] Ingrese otra carpeta (o 'q' para cancelar): ")
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
