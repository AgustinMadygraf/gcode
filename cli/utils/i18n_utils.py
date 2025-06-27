"""
Utilidades para la detección automática de idioma.
"""
import locale

def detect_language(args=None):
    if args and hasattr(args, 'lang') and args.lang:
        return args.lang
    sys_locale = locale.getdefaultlocale()[0] if hasattr(locale, 'getdefaultlocale') else None
    if sys_locale and sys_locale.lower().startswith('en'):
        return 'en'
    return 'es'
