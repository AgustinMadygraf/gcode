# Puerto para selección de archivos SVG
from abc import ABC, abstractmethod
from typing import Optional

class FileSelectorPort(ABC):
    @abstractmethod
    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite seleccionar un archivo SVG desde una ubicación dada.
        Retorna la ruta seleccionada o None si se cancela.
        """
        pass # noqa: W0107  # pylint: disable=unnecessary-pass
