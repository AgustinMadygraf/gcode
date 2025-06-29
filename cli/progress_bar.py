"""
Utilidad para mostrar una barra de progreso ASCII en terminal.
"""
import sys
import time
import logging
from cli.i18n import MESSAGES
from infrastructure.i18n.i18n_service import I18nService
from cli.utils.i18n_utils import detect_language

logger = logging.getLogger("progress_bar")
_last_percent_printed = {}

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█', print_end="\r", accessible=False, lang=None):
    global _last_percent_printed
    if accessible or not sys.stdout.isatty():
        percent = int((iteration / float(total)) * 100) if total else 100
        # Detectar idioma
        lang = lang or detect_language()
        i18n = I18nService(MESSAGES, default_lang=lang)
        # Evitar spam: solo imprimir si cambia el porcentaje
        key = (prefix, suffix, lang)
        if _last_percent_printed.get(key) != percent:
            print(i18n.get('progress_percent', lang=lang, percent=percent))
            _last_percent_printed[key] = percent
        if iteration == total:
            logger.info(f"{prefix} 100% {suffix}")
        return
    percent = (iteration / float(total)) * 100 if total else 100
    filled_length = int(length * iteration // total) if total else length
    bar = fill * filled_length + '-' * (length - filled_length)
    # No hay mensajes de usuario aquí, solo formato de barra. Si se agregan mensajes, usar i18n.
    # Si se agregan mensajes de usuario, usar i18n.get('clave')
    print(f'\r{prefix} |{bar}| {percent:3.0f}% {suffix}', end=print_end)
    if iteration == total:
        print()
