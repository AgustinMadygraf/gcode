"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

from cli.argument_parser import create_parser
from cli.factories.svg_to_gcode_app_factory import create_svg_to_gcode_app
from application.exceptions import AppError, InputValidationError, ProcessingError, OutputGenerationError
from infrastructure.factories.infra_factory import InfraFactory
import logging
import traceback

def main():
    parser = create_parser()
    args = parser.parse_args()
    # Configurar logger según modo dev
    logger = InfraFactory.get_logger()
    if getattr(args, 'dev', False):
        logger.setLevel(logging.DEBUG)
        logger.debug("[DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.")
    else:
        logger.setLevel(logging.WARNING)
    app = create_svg_to_gcode_app(args)
    try:
        return app.run()
    except InputValidationError as e:
        print(f"[ERROR] Validación de entrada: {e}")
        return 2
    except ProcessingError as e:
        print(f"[ERROR] Procesamiento: {e}")
        return 3
    except OutputGenerationError as e:
        print(f"[ERROR] Generación de salida: {e}")
        return 4
    except AppError as e:
        print(f"[ERROR] Error de aplicación: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        if getattr(args, 'dev', False):
            traceback.print_exc()
        return 99

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
