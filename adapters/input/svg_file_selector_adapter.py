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

    def __init__(self, logger, i18n=None):
        self.logger = logger
        self.i18n = i18n

    def _load_config(self):
        """Carga la configuración desde el archivo JSON."""
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.debug(f"Configuración cargada desde {self.CONFIG_PATH}: {config}")
            return config
        except FileNotFoundError as e:
            self.logger.error(f"Archivo de configuración no encontrado: {e}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error de decodificación JSON en la configuración: {e}")
            return {}
        except OSError as e:
            self.logger.error(f"Error de E/S al cargar configuración: {e}")
            return {}

    def _save_config(self, config):
        """Guarda la configuración en el archivo JSON."""
        try:
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Configuración guardada en {self.CONFIG_PATH}: {config}")
        except (OSError, json.JSONDecodeError) as e:
            self.logger.error(f"Error al guardar configuración: {e}")

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite al usuario seleccionar un archivo SVG desde la consola.
        Si no hay archivos, permite cambiar la carpeta de entrada o cancelar.
        """
        config = self._load_config()
        svg_input_dir = initial_dir or config.get('SVG_INPUT_DIR', './data/svg_input')
        while True:
            self.logger.debug(f"Buscando SVGs en: {svg_input_dir}")
            svg_files = _find_svg_files_recursively(svg_input_dir)
            self.logger.debug(f"SVGs encontrados: {svg_files}")
            if svg_files:
                self.logger.info(self.i18n.get("INFO_SVG_FILES_FOUND"))
                for idx, file in enumerate(svg_files, 1):
                    self.logger.option(f"  [{idx}] {file}")
                self.logger.option(self.i18n.get("OPTION_CANCEL"))
                try:
                    choice = int(input("[INPUT] " + self.i18n.get("PROMPT_SELECT_SVG_FILE")))
                except ValueError:
                    self.logger.warning(self.i18n.get("WARN_INVALID_OPTION"))
                    continue
                if choice == 0:
                    self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED"))
                    return None
                if 1 <= choice <= len(svg_files):
                    return svg_files[choice - 1]
                self.logger.warning(self.i18n.get("WARN_OUT_OF_RANGE"))
            else:
                self.logger.warning(self.i18n.get("WARN_NO_SVG_FOUND", svg_input_dir=svg_input_dir))
                self.logger.info(self.i18n.get("INFO_ASSIGN_NEW_DIR"))
                self.logger.info(self.i18n.get("INFO_RETRY"))
                self.logger.info(self.i18n.get("OPTION_CANCEL"))
                opt = input(self.i18n.get("PROMPT_SELECT_OPTION")).strip()
                if opt == '1':
                    new_dir = input(self.i18n.get("PROMPT_NEW_SVG_DIR")).strip()
                    self.logger.debug(f"Intentando cambiar directorio a: {new_dir}")
                    if os.path.isdir(new_dir):
                        svg_input_dir = new_dir
                        config['SVG_INPUT_DIR'] = new_dir
                        self._save_config(config)
                        self.logger.info(self.i18n.get("INFO_SVG_INPUT_UPDATED", new_dir=new_dir))
                    else:
                        self.logger.warning(self.i18n.get("WARN_INVALID_DIR"))
                elif opt == '2':
                    self.logger.info(self.i18n.get("INFO_PLACE_SVG_AND_RETRY"))
                    input()
                elif opt == '0':
                    self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED"))
                    return None
                else:
                    self.logger.warning(self.i18n.get("WARN_INVALID_OPTION"))
