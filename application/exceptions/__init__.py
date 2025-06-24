class AppError(Exception):
    """
    Excepción base para errores de aplicación.
    """
    pass

class DomainError(AppError):
    """
    Excepción para errores de dominio.
    """
    pass

class InfrastructureError(AppError):
    """
    Excepción para errores de infraestructura.
    """
    pass

# Importaciones para facilitar el acceso desde application.exceptions
from application.exceptions.use_case_exceptions import *

__all__ = [
    'AppError',
    'DomainError',
    'InfrastructureError',
    # Excepciones de casos de uso
    'UseCaseError',
    'InputValidationError',
    'ProcessingError',
    'OutputGenerationError',
    'TooManyOutputFilesError',
    'PathProcessingError',
    'InvalidInputFileError'
]
