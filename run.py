"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

import traceback

from cli.argument_parser import create_parser
from cli.factories.svg_to_gcode_app_factory import create_svg_to_gcode_app
from cli.i18n import MESSAGES
from cli.utils.i18n_utils import detect_language
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
    # Detectar idioma preferido
    lang = detect_language(args)

    class I18n:
        "Gestor de internacionalización"
        def __init__(self, messages, lang):
            self.messages = messages
            self.lang = lang
        def get(self, key, **kwargs):
            " Obtiene un mensaje internacionalizado por clave. "
            entry = self.messages.get(key)
            if not entry:
                return key
            template = entry.get(self.lang) or entry.get('es') or key
            try:
                return template.format(**kwargs)
            except (KeyError, ValueError, LookupError):
                return template

    i18n = I18n(MESSAGES, lang)

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
    logger.debug(i18n.get("STARTING_MSG"))
    # Ejemplo de advertencia por argumento obsoleto
    if hasattr(args, 'foo') and getattr(args, 'foo', None) is not None:
        logger.warning(
            i18n.get("WARN_ARG_FOO_DEPRECATED")
            if "WARN_ARG_FOO_DEPRECATED" in MESSAGES
            else (
                "El argumento '--foo' "
                "está obsoleto y será ignorado."
            )
        )
    if getattr(args, 'dev', False):
        logger.debug(i18n.get("DEBUG_DEV_MODE_ON"))
    app = create_svg_to_gcode_app(args, container=container)
    try:
        result = app.run()
        logger.info(i18n.get("INFO_PROCESSING_DONE"))
        return result
    except InputValidationError as e:
        logger.error(
            i18n.get(
                "ERROR_INVALID_INPUT",
                error=str(e)
            ) if "ERROR_INVALID_INPUT" in MESSAGES
            else (
                "Validación de entrada: "
                f"{e}"
            )
        )
        return 2
    except ProcessingError as e:
        logger.error(
            i18n.get(
                "ERROR_GENERIC",
                error=str(e)
            )
            if "ERROR_GENERIC" in MESSAGES
            else (
                "Procesamiento: "
                f"{e}"
            )
        )
        return 3
    except OutputGenerationError as e:
        logger.error(
            i18n.get(
                "ERROR_OUTPUT_GEN",
                error=str(e)
            )
            if "ERROR_OUTPUT_GEN" in MESSAGES
            else (
                "Generación de salida: "
                f"{e}"
            )
        )
        return 4
    except AppError as e:
        logger.error(
            i18n.get(
                "ERROR_GENERIC",
                error=str(e)
            )
            if "ERROR_GENERIC" in MESSAGES
            else (
                "Error de aplicación: "
                f"{e}"
            )
        )
        return 1
    except RuntimeError as e:
        logger.error(
            i18n.get(
                "ERROR_GENERIC",
                error=str(e)
            )
            if "ERROR_GENERIC" in MESSAGES
            else (
                "Error inesperado de ejecución: "
                f"{e}"
            )
        )
        if getattr(args, 'dev', False):
            tb_str = traceback.format_exc()
            logger.error(tb_str)
        return 99

if __name__ == "__main__":
    EXIT_CODE = main()
    exit(EXIT_CODE)
