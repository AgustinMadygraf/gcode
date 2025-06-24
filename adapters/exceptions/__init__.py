"""
Excepciones de adaptadores para el proyecto GCode.
Define la jerarquía de excepciones para la capa de adaptadores.
"""
from application.exceptions import AppError

class AdapterError(AppError):
    """
    Excepción base para errores en adaptadores.
    """
    pass

class InputAdapterError(AdapterError):
    """
    Excepción para errores en adaptadores de entrada.
    """
    pass

class OutputAdapterError(AdapterError):
    """
    Excepción para errores en adaptadores de salida.
    """
    pass

# Subclases específicas
class SVGParsingError(InputAdapterError):
    """Excepción para errores en el parsing de archivos SVG."""
    pass

class InvalidSVGError(InputAdapterError):
    """Excepción para archivos SVG con estructura inválida."""
    pass

class GCodeGenerationError(OutputAdapterError):
    """Excepción para errores en la generación de G-code."""
    pass

class LoggingError(OutputAdapterError):
    """Excepción para errores en el sistema de logging."""
    pass

# Exportar todas las excepciones
__all__ = [
    'AdapterError',
    'InputAdapterError',
    'OutputAdapterError',
    'SVGParsingError',
    'InvalidSVGError',
    'GCodeGenerationError',
    'LoggingError'
]
