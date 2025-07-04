from cli.presenters.cli_presenter import CliPresenter
from cli.terminal_colors import TerminalColors
from cli.utils.terminal_utils import supports_color
from infrastructure.factories.logger_factory import LoggerFactory
import sys
import os

if __name__ == "__main__":
    # Crear logger local para demo
    logger = LoggerFactory.create_logger("demo_colored_output", use_color=True, level="DEBUG", show_file_line=True)
    # Mostrar información de entorno
    logger.info(f"Sistema operativo: {os.name}")
    logger.info(f"Terminal: {os.environ.get('TERM_PROGRAM', 'N/A')}")
    logger.info(f"sys.stdout.isatty(): {getattr(sys.stdout, 'isatty', lambda: False)()}")
    logger.info(f"Soporte de color detectado: {supports_color()}")

    color_service = TerminalColors(use_colors=True)
    presenter = CliPresenter(i18n=None, color_service=color_service, logger_instance=logger)
    logger.info("\n--- Ejemplo de salida con colores y modo normal ---")
    presenter.print_debug("Mensaje de debug visible solo en modo dev")
    presenter.print_success("Operación completada correctamente")
    presenter.print_warning("Esto es una advertencia")
    presenter.print_error("Ocurrió un error grave")

    logger.info("\n--- Ejemplo de salida en modo dev (archivo y línea) ---")
    presenter.print_debug("Debug detallado", file="test.py", line=42, dev_mode=True)
    presenter.print_success("Éxito con contexto", file="test.py", line=43, dev_mode=True)
    presenter.print_warning("Advertencia con contexto", file="test.py", line=44, dev_mode=True)
    presenter.print_error("Error con contexto", file="test.py", line=45, dev_mode=True)
