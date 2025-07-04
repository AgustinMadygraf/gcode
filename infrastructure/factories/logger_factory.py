"""
Factory para estandarizar la creación de loggers en toda la aplicación.
"""
from infrastructure.logger import get_logger
from domain.ports.logger_port import LoggerPort

class LoggerFactory:
    @staticmethod
    def create_logger(
        context_name: str = None,
        use_color: bool = True,
        level: str = 'INFO',
        show_file_line: bool = False
    ) -> LoggerPort:
        """
        Crea un logger contextual estandarizado para un componente específico.
        Args:
            context_name: Nombre del contexto o componente (opcional)
            use_color: Si se deben usar colores ANSI
            level: Nivel de logging ('DEBUG', 'INFO', etc.)
            show_file_line: Si se debe mostrar archivo:línea en cada mensaje
        Returns:
            Un logger configurado que implementa LoggerPort
        """
        # Por ahora, context_name no se usa, pero puede usarse para prefijos personalizados
        return get_logger(
            use_color=use_color,
            level=level,
            show_file_line=show_file_line
        )
