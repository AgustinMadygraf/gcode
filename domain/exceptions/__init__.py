"""
Excepciones de dominio para el proyecto GCode.
Define la jerarquía de excepciones para la capa de dominio.
"""
from application.exceptions import DomainError

class ValidationError(DomainError):
    """
    Excepción para errores de validación en entidades o value objects.
    """
    pass

class BusinessRuleError(DomainError):
    """
    Excepción para violaciones de reglas de negocio.
    """
    pass

class GeometryError(DomainError):
    """
    Excepción para errores en operaciones geométricas.
    """
    pass

class TransformationError(DomainError):
    """
    Excepción para errores en transformaciones de rutas.
    """
    pass

# Subclases de errores de validación
class InvalidPointError(ValidationError):
    """Excepción para puntos con coordenadas inválidas."""
    pass

class InvalidSegmentError(ValidationError):
    """Excepción para segmentos con geometría inválida."""
    pass

class InvalidPathError(ValidationError):
    """Excepción para rutas incorrectamente definidas."""
    pass

class InvalidScaleError(GeometryError):
    """Excepción para errores de escalado."""
    pass

# Exportar todas las excepciones
__all__ = [
    'ValidationError', 
    'BusinessRuleError', 
    'GeometryError',
    'TransformationError',
    'InvalidPointError',
    'InvalidSegmentError',
    'InvalidPathError',
    'InvalidScaleError'
]
