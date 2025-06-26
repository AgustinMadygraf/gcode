"""
Servicio de internacionalización desacoplado de la UI.
"""
from typing import Dict

class I18nService:
    def __init__(self, messages: Dict[str, Dict[str, str]], default_lang: str = "es"):
        self._messages = messages
        self._default_lang = default_lang

    def get(self, key: str, lang: str = None, **kwargs) -> str:
        lang = lang or self._default_lang
        msg = self._messages.get(lang, {}).get(key) or self._messages.get(self._default_lang, {}).get(key) or key
        if kwargs:
            try:
                return msg.format(**kwargs)
            except Exception:
                return msg
        return msg
