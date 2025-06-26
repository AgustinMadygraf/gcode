"""
ConfigManager centraliza la carga, acceso y actualización de la configuración de usuario y de la aplicación.
"""
import json
from cli.user_config import UserConfig

class ConfigManager:
    def __init__(self, args=None):
        self.user_config = UserConfig()
        self.args = args
        self._load_user_preferences()
        self._override_args_with_preferences()
        if args and getattr(args, 'save_config', False):
            self.user_config.update_from_args(args)

    def _load_user_preferences(self):
        if self.args and getattr(self.args, 'config', None):
            try:
                with open(self.args.config, 'r', encoding='utf-8') as f:
                    self.user_config.data.update(json.load(f))
            except Exception:
                pass

    def _override_args_with_preferences(self):
        if self.args:
            for key in ["lang", "no_color", "input", "output"]:
                if getattr(self.args, key, None) is None and self.user_config.get(key) is not None:
                    setattr(self.args, key, self.user_config.get(key))

    def get(self, key, default=None):
        return self.user_config.get(key, default)

    def update_from_args(self, args):
        self.user_config.update_from_args(args)

    def save(self, path=None):
        self.user_config.save(path)
