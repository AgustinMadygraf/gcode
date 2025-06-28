from cli.presenters.cli_presenter import CliPresenter
from cli.terminal_colors import TerminalColors
from cli.utils.terminal_utils import supports_color
import sys
import os

if __name__ == "__main__":
    # Mostrar información de entorno
    print(f"Sistema operativo: {os.name}")
    print(f"Terminal: {os.environ.get('TERM_PROGRAM', 'N/A')}")
    print(f"sys.stdout.isatty(): {getattr(sys.stdout, 'isatty', lambda: False)()}")
    print(f"Soporte de color detectado: {supports_color()}")

    color_service = TerminalColors(use_colors=True)
    presenter = CliPresenter(i18n=None, color_service=color_service)
    print("\n--- Ejemplo de salida con colores y modo normal ---")
    presenter.print_debug("Mensaje de debug visible solo en modo dev")
    presenter.print_success("Operación completada correctamente")
    presenter.print_warning("Esto es una advertencia")
    presenter.print_error("Ocurrió un error grave")

    print("\n--- Ejemplo de salida en modo dev (archivo y línea) ---")
    presenter.print_debug("Debug detallado", file="test.py", line=42, dev_mode=True)
    presenter.print_success("Éxito con contexto", file="test.py", line=43, dev_mode=True)
    presenter.print_warning("Advertencia con contexto", file="test.py", line=44, dev_mode=True)
    presenter.print_error("Error con contexto", file="test.py", line=45, dev_mode=True)
