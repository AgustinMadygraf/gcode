"""
Módulo para gestionar la configuración de usuario persistente para simple_svg2gcode.
"""
import os
import json
from pathlib import Path

CONFIG_FILENAME = ".svg2gcode_config.json"

class UserConfig:
    def __init__(self):
        self.config_path = Path.home() / CONFIG_FILENAME
        self.data = {}
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def update_from_args(self, args):
        # Guarda solo preferencias relevantes
        for key in ["lang", "no_color", "input", "output"]:
            if hasattr(args, key):
                self.data[key] = getattr(args, key)
        self.save()
