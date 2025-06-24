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
