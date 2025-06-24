"""
Inicialización del paquete de manejo de errores.
"""

from infrastructure.error_handling.error_handler import ErrorHandler
from infrastructure.error_handling.exception_decorator import ExceptionHandler

__all__ = ['ErrorHandler', 'ExceptionHandler']
