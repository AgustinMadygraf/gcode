"""
Adaptador CLI para la selección de archivos SVG.
Implementa FileSelectorPort y permite al usuario elegir un archivo SVG desde la consola.
Guarda y recupera la carpeta de entrada desde un archivo de configuración JSON.
"""
from domain.ports.file_selector_port import FileSelectorPort
from typing import Optional
import os
import json
from pathlib import Path
from infrastructure.logger import logger

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
    Permite al usuario navegar y seleccionar archivos SVG, y actualiza la configuración de la carpeta de entrada.
    """
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../infrastructure/config/config.json')

    def _load_config(self):
        """Carga la configuración desde el archivo JSON."""
        with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self, config):
        """Guarda la configuración en el archivo JSON."""
        with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Permite al usuario seleccionar un archivo SVG desde la consola.
        Si no hay archivos, permite cambiar la carpeta de entrada o cancelar.
        """
        config = self._load_config()
        svg_input_dir = initial_dir or config.get('SVG_INPUT_DIR', './data/svg_input')
        while True:
            svg_files = _find_svg_files_recursively(svg_input_dir)
            if svg_files:
                logger.info("Archivos SVG encontrados:")
                for idx, file in enumerate(svg_files, 1):
                    logger.option(f"  [{idx}] {file}")
                logger.option("  [0] Cancelar")
                try:
                    choice = int(input("[INPUT] Seleccione un archivo SVG por número: "))
                except ValueError:
                    logger.warning("Opción inválida.")
                    continue
                if choice == 0:
                    logger.info("Operación cancelada por el usuario.")
                    return None
                if 1 <= choice <= len(svg_files):
                    return svg_files[choice - 1]
                logger.warning("Selección fuera de rango.")
            else:
                logger.warning(f"No se encontraron archivos SVG en '{svg_input_dir}'.")
                logger.info("1) Asignar nueva carpeta de entrada")
                logger.info("2) Reintentar (debe colocar un archivo SVG en la carpeta actual)")
                logger.info("0) Cancelar")
                opt = input("Seleccione una opción: ").strip()
                if opt == '1':
                    new_dir = input("Ingrese la nueva ruta de carpeta para SVGs: ").strip()
                    if os.path.isdir(new_dir):
                        svg_input_dir = new_dir
                        config['SVG_INPUT_DIR'] = new_dir
                        self._save_config(config)
                        logger.info(f"SVG_INPUT_DIR actualizado a: {new_dir}")
                    else:
                        logger.warning("Carpeta no válida.")
                elif opt == '2':
                    logger.info("Por favor, coloque al menos un archivo SVG en la carpeta y presione Enter para reintentar.")
                    input()
                elif opt == '0':
                    logger.info("Operación cancelada por el usuario.")
                    return None
                else:
                    logger.warning("Opción inválida.")
