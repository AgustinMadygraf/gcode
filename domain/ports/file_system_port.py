"""
Puerto FileSystemPort: interfaz para operaciones de archivos en el dominio.
"""

from abc import ABC, abstractmethod
from typing import Any

class FileSystemPort(ABC):
    """
    Interfaz para leer y escribir archivos desde el dominio.
    """

    @abstractmethod
    def read(self, file_path: str) -> Any:
        """Leer el archivo en la ruta especificada.

        Args:
            file_path (str): La ruta del archivo a leer.

        Returns:
            Any: El contenido del archivo.
        """
        pass

    @abstractmethod
    def write(self, file_path: str, data: Any) -> None:
        """Escribir datos en el archivo en la ruta especificada.

        Args:
            file_path (str): La ruta del archivo donde se escribirán los datos.
            data (Any): Los datos a escribir en el archivo.
        """
        pass
