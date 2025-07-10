"""
Adaptador CLI para la selección de archivos SVG.
Implementa FileSelectorPort y permite al usuario elegir un archivo SVG desde la consola.
Guarda y recupera la carpeta de entrada desde un archivo de configuración JSON.
"""
import os
import json
from typing import Optional
from domain.ports.file_selector_port import FileSelectorPort

def _find_svg_files_recursively(directory: str):
    """Busca archivos SVG de forma recursiva en el directorio dado."""
    svg_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.svg'):
                svg_files.append(os.path.join(root, file))
    return svg_files

class SvgFileSelectorAdapter(FileSelectorPort):
    """
    Adaptador para la selección de archivos SVG desde la CLI.
    Permite al usuario navegar y seleccionar archivos SVG,
    y actualiza la configuración de la carpeta de entrada.
    """
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../infrastructure/config/config.json')

    DEBUG_ENABLED = True
    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def __init__(self, logger, i18n=None):
        self.logger = logger
        self.i18n = i18n

    def _load_config(self):
        """Carga la configuración desde el archivo JSON."""
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self._debug(self.i18n.get('DEBUG_CONFIG_LOADED', path=self.CONFIG_PATH, config=config))
            return config
        except FileNotFoundError as e:
            self.logger.error(self.i18n.get('ERROR_CONFIG_NOT_FOUND', error=str(e)))
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(self.i18n.get('ERROR_CONFIG_JSON', error=str(e)))
            return {}
        except OSError as e:
            self.logger.error(self.i18n.get('ERROR_CONFIG_IO', error=str(e)))
            return {}

    def _save_config(self, config):
        """Guarda la configuración en el archivo JSON."""
        try:
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self._debug(self.i18n.get('DEBUG_CONFIG_SAVED', path=self.CONFIG_PATH, config=config))
        except (OSError, json.JSONDecodeError) as e:
            self.logger.error(self.i18n.get('ERROR_SAVE_CONFIG', error=str(e)))

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        # Stub para cumplir con la interfaz, no se usa en este adaptador
        print("This method is not implemented in GcodeFileSelectorAdapter.")
        return None
