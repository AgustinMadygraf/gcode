"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

import traceback

from cli.argument_parser import create_parser
from cli.main import SvgToGcodeApp
from cli.i18n import MESSAGES
from cli.utils.i18n_utils import detect_language
from application.exceptions import (
    AppError,
    InputValidationError,
    ProcessingError,
    OutputGenerationError,
)
from infrastructure.factories.infra_factory import InfraFactory
from infrastructure.factories.container import Container
from infrastructure.i18n.i18n_service import I18nService

def main():
    " Punto de entrada principal de la aplicación. "
    parser = create_parser()
    args = parser.parse_args()
    lang = detect_language(args)
    i18n = I18nService(MESSAGES, lang)
    use_color = not getattr(args, 'no_color', False)
    log_level = 'DEBUG' if getattr(args, 'dev', False) else 'INFO'
    show_file_line = getattr(args, 'dev', False)
    logger = InfraFactory.get_logger(
        use_color=use_color,
        level=log_level,
        show_file_line=show_file_line
    )
    logger.info(f"Nivel de log configurado: {log_level}")
    container = Container( logger=logger, i18n=i18n)
    logger.debug(i18n.get("STARTING_MSG"))
    if getattr(args, 'dev', False):
        logger.debug(i18n.get("DEBUG_DEV_MODE_ON"))
    app = SvgToGcodeApp(args, container=container)
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
            logger.error(i18n.get('ERROR_TRACEBACK') if 'ERROR_TRACEBACK' in MESSAGES else 'Traceback:')
            logger.error(tb_str)
        return 99

if __name__ == "__main__":
    EXIT_CODE = main()
    exit(EXIT_CODE)
