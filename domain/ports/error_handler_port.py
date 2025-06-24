"""
Puerto para el sistema de manejo de errores.
Define la interfaz que debe implementar cualquier manejador de errores.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Type
from application.exceptions import AppError

class ErrorHandlerPort(ABC):
    """
    Puerto para manejadores de errores.
    Define la interfaz para el sistema de manejo de errores transversal.
    """
    @abstractmethod
    def handle(self, ex: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Maneja una excepción y devuelve información estructurada sobre el error.
        """
        pass
    
    @abstractmethod
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """
        Registra un manejador para un tipo específico de excepción.
        """
        pass
    
    @abstractmethod
    def wrap_execution(self, func: Callable, context: Dict[str, Any] = None):
        """
        Envuelve una función con manejo de excepciones.
        """
        pass
