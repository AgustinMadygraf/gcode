"""
Excepciones para casos de uso de la aplicación.
"""
from application.exceptions import AppError

class UseCaseError(AppError):
    """
    Excepción base para errores en casos de uso.
    """
    pass

class InputValidationError(UseCaseError):
    """
    Excepción para errores de validación de entrada en un caso de uso.
    """
    pass

class ProcessingError(UseCaseError):
    """
    Excepción para errores durante el procesamiento de un caso de uso.
    """
    pass

class OutputGenerationError(UseCaseError):
    """
    Excepción para errores en la generación de salida de un caso de uso.
    """
    pass

# Subclases específicas
class TooManyOutputFilesError(OutputGenerationError):
    """Excepción para cuando se superan los límites de archivos de salida."""
    pass

class PathProcessingError(ProcessingError):
    """Excepción para errores en el procesamiento de paths."""
    pass

class InvalidInputFileError(InputValidationError):
    """Excepción para archivos de entrada inválidos."""
    pass

# Exportar todas las excepciones
__all__ = [
    'UseCaseError',
    'InputValidationError',
    'ProcessingError',
    'OutputGenerationError',
    'TooManyOutputFilesError',
    'PathProcessingError',
    'InvalidInputFileError'
]
