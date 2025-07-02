"""
Servicio de internacionalización desacoplado de la UI.
"""
from typing import Dict

class I18nService:
    def __init__(self, messages: Dict[str, Dict[str, dict]], default_lang: str = "es"):
        """
        messages: Dict[str, Dict[str, str]]
            Estructura esperada: clave → idioma → valor
        """
        self._messages = messages
        self._default_lang = default_lang

    def get(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Obtiene el mensaje localizado para la clave y el idioma dados.
        Si no existe para el idioma solicitado, intenta con el idioma por defecto.
        Si no existe la clave, devuelve la clave como fallback.
        """
        lang = lang or self._default_lang
        entry = self._messages.get(key)
        if not entry:
            return key
        msg = entry.get(lang) or entry.get(self._default_lang) or key
        if kwargs:
            try:
                return msg.format(**kwargs)
            except Exception:
                return msg
        return msg
