"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

from cli.argument_parser import create_parser
from cli.factories.svg_to_gcode_app_factory import create_svg_to_gcode_app
from application.exceptions import AppError, InputValidationError, ProcessingError, OutputGenerationError
from infrastructure.factories.infra_factory import InfraFactory
from infrastructure.logger import logger

def main():
    parser = create_parser()
    args = parser.parse_args()
    # Configurar logger según modo dev
    logger = InfraFactory.get_logger()
    if getattr(args, 'dev', False):
        logger.set_level('DEBUG')
        logger.debug("[DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.")
    else:
        logger.set_level('INFO')  # Mostrar menús y opciones siempre
    app = create_svg_to_gcode_app(args)
    try:
        return app.run()
    except InputValidationError as e:
        logger.error(f"Validación de entrada: {e}")
        return 2
    except ProcessingError as e:
        logger.error(f"Procesamiento: {e}")
        return 3
    except OutputGenerationError as e:
        logger.error(f"Generación de salida: {e}")
        return 4
    except AppError as e:
        logger.error(f"Error de aplicación: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        if getattr(args, 'dev', False):
            import traceback
            traceback.print_exc()
        return 99

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
