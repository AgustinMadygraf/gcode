"""
Puerto FileSystemPort: interfaz para operaciones de archivos en el dominio.
"""
from abc import ABC, abstractmethod
from typing import Any

class FileSystemPort(ABC):
    @abstractmethod
    def read(self, file_path: str) -> Any:
        pass

    @abstractmethod
    def write(self, file_path: str, data: Any) -> None:
        pass
