"""
Excepciones de infraestructura para el proyecto GCode.
Define la jerarquía de excepciones para la capa de infraestructura.
"""
from application.exceptions import InfrastructureError

class ConfigurationError(InfrastructureError):
    """
    Excepción para errores de configuración.
    """
    pass

class FileSystemError(InfrastructureError):
    """
    Excepción para errores de sistema de archivos.
    """
    pass

class DependencyError(InfrastructureError):
    """
    Excepción para errores en la inyección de dependencias.
    """
    pass

class TransformStrategyError(InfrastructureError):
    """
    Excepción para errores en estrategias de transformación.
    """
    pass

# Subclases específicas
class MissingDependencyError(DependencyError):
    """Excepción para dependencias no inyectadas."""
    pass

class SVGFileNotFoundError(FileSystemError):
    """Excepción para archivos SVG no encontrados."""
    pass

class InvalidConfigurationError(ConfigurationError):
    """Excepción para configuración inválida."""
    pass

# Exportar todas las excepciones
__all__ = [
    'ConfigurationError',
    'FileSystemError',
    'DependencyError',
    'TransformStrategyError',
    'MissingDependencyError',
    'SVGFileNotFoundError',
    'InvalidConfigurationError'
]
