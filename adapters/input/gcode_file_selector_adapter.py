"""
Path: adapters/input/gcode_file_selector_adapter.py
Adaptador para selección de archivos GCODE desde la consola.
"""

import os
from pathlib import Path
from typing import Optional, List
from domain.ports.file_selector_port import FileSelectorPort

class GcodeFileSelectorAdapter(FileSelectorPort):
    """Adaptador para selección de archivos GCODE desde la consola."""
    def __init__(self, config_provider=None, i18n=None, logger=None):
        self.config_provider = config_provider
        self.i18n = i18n
        self.logger = logger

    def _debug(self, message):
        "Muestra mensajes de debug solo si el flag 'GcodeFileSelectorAdapter' está activado en la configuración."
        debug_enabled = False
        if self.config_provider and hasattr(self.config_provider, "get_debug_flag"):
            debug_enabled = self.config_provider.get_debug_flag("GcodeFileSelectorAdapter")
        if debug_enabled:
            if self.logger and hasattr(self.logger, "debug"):
                self.logger.debug(message)
            else:
                print(f"[DEBUG] {message}")

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite al usuario seleccionar un archivo SVG desde la consola.
        Si no hay archivos, permite cambiar la carpeta de entrada o cancelar.
        """
        config = self._load_config()
        svg_input_dir = initial_dir or config.get('SVG_INPUT_DIR', './data/svg_input')
        print(f"[DEBUG] Buscando SVGs en: {svg_input_dir}")
        while True:
            self._debug(self.i18n.get('DEBUG_SEARCHING_SVGS', dir=svg_input_dir))
            svg_files = self._find_svg_files_recursively(svg_input_dir)
            self._debug(self.i18n.get('DEBUG_SVGS_FOUND', files=svg_files))
            if svg_files:
                self.logger.info(self.i18n.get("INFO_SVG_FILES_FOUND"))
                for idx, file in enumerate(svg_files, 1):
                    self.logger.option(self.i18n.get('OPTION_SVG_FILE', num=idx, filename=file))
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
                self.logger.warning(self.i18n.get('WARN_OUT_OF_RANGE'))
            else:
                self.logger.warning(self.i18n.get("WARN_NO_SVG_FOUND", svg_input_dir=svg_input_dir))
                self.logger.info(self.i18n.get('INFO_ASSIGN_NEW_DIR'))
                self.logger.info(self.i18n.get('INFO_RETRY'))
                self.logger.info(self.i18n.get('INFO_PLACE_SVG_AND_RETRY'))
                self.logger.info(self.i18n.get("OPTION_CANCEL"))
                opt = input(self.i18n.get("PROMPT_SELECT_OPTION")).strip()
                if opt == '1':
                    new_dir = input(self.i18n.get('PROMPT_NEW_SVG_DIR')).strip()
                    self._debug(self.i18n.get('DEBUG_CHANGING_DIR', dir=new_dir))
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

    def select_gcode_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite al usuario seleccionar un archivo GCODE desde la consola.
        """
        config = self._load_config()
        gcode_dir = initial_dir or config.get('GCODE_OUTPUT_DIR', './data/gcode_output')
        while True:
            gcode_files = self._find_gcode_files_recursively(gcode_dir)
            if gcode_files:
                self.logger.info(self.i18n.get("INFO_GCODE_FILES_FOUND"))
                for idx, file in enumerate(gcode_files, 1):
                    self.logger.option(f"  [{idx}] {file}")
                self.logger.option(self.i18n.get("OPTION_CANCEL"))
                try:
                    choice = int(input("[INPUT] " + self.i18n.get("PROMPT_SELECT_GCODE_FILE")))
                    if choice == 0:
                        self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED"))
                        return None
                    if 1 <= choice <= len(gcode_files):
                        return gcode_files[choice - 1]
                    self.logger.warning(self.i18n.get("WARN_INVALID_OPTION"))
                except ValueError:
                    self.logger.warning(self.i18n.get("WARN_INVALID_NUMBER"))
                except KeyboardInterrupt:
                    self.logger.info(self.i18n.get("INFO_OPERATION_CANCELLED_CTRL_C"))
                    return None
            else:
                self.logger.warning(self.i18n.get("WARN_NO_GCODE_FOUND", gcode_dir=gcode_dir))
                new_dir = input(self.i18n.get("PROMPT_NEW_GCODE_DIR"))
                if new_dir.lower() == 'q':
                    return None
                gcode_dir = new_dir

    def _find_gcode_files_recursively(self, directory: str) -> List[str]:
        path = Path(directory)
        if not path.exists():
            return []
        result = []
        for item in path.glob('**/*.gcode'):
            if item.is_file():
                result.append(str(item))
        return sorted(result)

    def _load_config(self):
        if self.config_provider:
            return self.config_provider
        return {}

    def _find_svg_files_recursively(self, directory: str) -> List[str]:
        path = Path(directory)
        if not path.exists():
            return []
        result = []
        for item in path.glob('**/*.svg'):
            if item.is_file():
                result.append(str(item))
        return sorted(result)

    def _save_config(self, config):
        """
        Guarda la configuración si config_provider lo soporta.
        """
        if hasattr(self.config_provider, "save"):
            self.config_provider.save(config)
        else:
            self._debug("No se puede guardar la configuración: config_provider no soporta 'save'.")
