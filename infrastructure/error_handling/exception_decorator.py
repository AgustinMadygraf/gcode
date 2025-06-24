"""
Decorador para manejo de excepciones.
"""
import functools
from typing import Dict, Any, Callable, Optional
from domain.ports.error_handler_port import ErrorHandlerPort

class ExceptionHandler:
    """
    Decorador para manejar excepciones en métodos de las capas aplicación y dominio.
    """
    def __init__(self, error_handler: ErrorHandlerPort, context_provider: Optional[Callable[..., Dict[str, Any]]] = None):
        """
        Inicializa el decorador.
        
        Args:
            error_handler: Implementación de ErrorHandlerPort para manejar excepciones
            context_provider: Función opcional que devuelve contexto adicional para el manejo de errores
        """
        self.error_handler = error_handler
        self.context_provider = context_provider
    
    def __call__(self, func):
        """
        Aplica el decorador a una función o método.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener contexto adicional si hay un proveedor
            context = {}
            if self.context_provider:
                context = self.context_provider(*args, **kwargs)
            
            # Ejecutar la función original envuelta en el manejador de errores
            return self.error_handler.wrap_execution(
                lambda: func(*args, **kwargs), 
                context
            )
        return wrapper
