"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

import traceback

from cli.argument_parser import create_parser
from cli.factories.svg_to_gcode_app_factory import create_svg_to_gcode_app
from application.exceptions import (
    AppError,
    InputValidationError,
    ProcessingError,
    OutputGenerationError,
)
from infrastructure.factories.infra_factory import InfraFactory
from infrastructure.factories.dependency_container import DependencyContainer

def main():
    " Punto de entrada principal de la aplicación. "
    parser = create_parser()
    args = parser.parse_args()
    # Configurar logger según modo dev y color
    use_color = not getattr(args, 'no_color', False)
    log_level = 'DEBUG' if getattr(args, 'dev', False) else 'INFO'
    show_file_line = getattr(args, 'dev', False)
    logger = InfraFactory.get_logger(
        use_color=use_color,
        level=log_level,
        show_file_line=show_file_line
    )
    container = DependencyContainer(logger=logger)
    logger.info("Iniciando aplicación SVG2GCODE")
    # Ejemplo de advertencia por argumento obsoleto
    if hasattr(args, 'foo') and getattr(args, 'foo', None) is not None:
        logger.warning("El argumento '--foo' está obsoleto y será ignorado.")
    if getattr(args, 'dev', False):
        logger.debug("Modo desarrollador activo: logging DEBUG y stacktrace extendido.")
    app = create_svg_to_gcode_app(args, container=container)
    try:
        result = app.run()
        logger.info("Ejecución finalizada correctamente")
        return result
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
    except RuntimeError as e:
        logger.error(f"Error inesperado de ejecución: {e}")
        if getattr(args, 'dev', False):
            tb_str = traceback.format_exc()
            logger.error(tb_str)
        return 99

if __name__ == "__main__":
    EXIT_CODE = main()
    exit(EXIT_CODE)
