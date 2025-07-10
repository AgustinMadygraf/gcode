"""
Manejador de excepciones transversal para el proyecto GCode.
"""
import traceback
from typing import Callable, Dict, Type, Any
from application.exceptions import DomainError, InfrastructureError
from domain.ports.logger_port import LoggerPort

class ErrorHandler:
    """
    Manejador de excepciones transversal para toda la aplicación.
    Proporciona una forma unificada de manejar excepciones según su tipo.
    """
    def __init__(self, logger: LoggerPort):
        self.logger = logger
        self.handlers: Dict[Type[Exception], Callable] = {}

        # Registrar handlers por defecto para tipos de excepciones comunes
        self.register_default_handlers()

    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """
        Registra un manejador para un tipo específico de excepción.
        """
        self.handlers[exception_type] = handler

    def register_default_handlers(self):
        """
        Registra los manejadores por defecto para los tipos principales de excepciones.
        """
        # Excepciones base
        self.register_handler(DomainError, self._handle_domain_error)
        self.register_handler(InfrastructureError, self._handle_infrastructure_error)
        self.register_handler(Exception, self._handle_generic_error)

    def _handle_domain_error(self, ex: DomainError, context: Dict[str, Any] = None):
        """Manejador para excepciones de dominio."""
        self.logger.error(f"Error de dominio: {str(ex)}")
        context = context or {}
        # El dominio no debería exponer detalles técnicos al usuario
        return {
            "error": "Error en la lógica de negocio",
            "message": str(ex),
            "context": context
        }

    def _handle_infrastructure_error(self, ex: InfrastructureError, context: Dict[str, Any] = None):
        """Manejador para excepciones de infraestructura."""
        self.logger.error(f"Error de infraestructura: {str(ex)}")
        self.logger.debug(traceback.format_exc())
        context = context or {}
        return {
            "error": "Error técnico interno",
            "message": str(ex),
            "context": context
        }

    def _handle_generic_error(self, ex: Exception, context: Dict[str, Any] = None):
        """Manejador para excepciones genéricas no controladas."""
        self.logger.error(f"Error no controlado: {str(ex)}")
        self.logger.error(traceback.format_exc())
        context = context or {}
        return {
            "error": "Error interno",
            "message": "Se ha producido un error inesperado",
            "context": context
        }

    def handle(self, ex: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Maneja una excepción utilizando el handler correspondiente registrado.
        Si no hay un handler específico, busca en la cadena de herencia.
        """
        context = context or {}

        # Buscar el handler más específico
        for exception_class in ex.__class__.__mro__:
            if exception_class in self.handlers:
                return self.handlers[exception_class](ex, context)

        # Si no se encuentra handler, usar el genérico
        return self._handle_generic_error(ex, context)

    def wrap_execution(self, func: Callable, context: Dict[str, Any] = None):
        """
        Envuelve una función con manejo de excepciones.
        Útil para endpoints o comandos CLI.
        """
        try:
            return {
                "success": True,
                "result": func()
            }
        # Catch specific known exceptions first
        except (DomainError, InfrastructureError) as ex:
            error_result = self.handle(ex, context)
            return {
                "success": False,
                **error_result
            }
        except Exception as ex:
            error_result = self.handle(ex, context)
            self.logger.critical("Unhandled exception occurred", exc_info=True)
            raise
