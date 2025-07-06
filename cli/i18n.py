"""
Diccionario de mensajes para internacionalización CLI.
Organizado por etiqueta → idioma → valor para mejor mantenibilidad.
"""

import json
import os


# Cargar mensajes desde JSON externo
_i18n_json_path = os.path.join(os.path.dirname(__file__), 'i18n.json')
with open(_i18n_json_path, encoding='utf-8') as f:
    MESSAGES = json.load(f)

def get_message(key, lang='es', **kwargs):
    """Obtiene el mensaje localizado y formatea con kwargs si aplica."""
    # Si la clave no existe, devolver la propia clave como fallback
    if key not in MESSAGES:
        return key

    # Si el idioma no existe para esa clave, intentar con el idioma por defecto (es)
    message_template = MESSAGES[key].get(lang, MESSAGES[key].get('es', key))

    # Aplicar formato si hay argumentos
    if kwargs:
        try:
            return message_template.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            return message_template

    return message_template
