from pathlib import Path
from typing import Optional, List
from domain.ports.file_selector_port import FileSelectorPort

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
                print("\nArchivos GCODE encontrados:")
                for idx, file in enumerate(gcode_files, 1):
                    print(f"  [{idx}] {file}")
                print("  [0] Cancelar")
                try:
                    choice = int(input("\nSeleccione un archivo GCODE por número: "))
                    if choice == 0:
                        print("Operación cancelada por el usuario.")
                        return None
                    if 1 <= choice <= len(gcode_files):
                        return gcode_files[choice - 1]
                    print("Opción inválida.")
                except ValueError:
                    print("Por favor, ingrese un número válido.")
            else:
                print(f"No se encontraron archivos GCODE en {gcode_dir}")
                new_dir = input("Ingrese otra carpeta (o 'q' para cancelar): ")
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
