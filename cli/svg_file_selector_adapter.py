# Adaptador CLI para FileSelectorPort
from domain.ports.file_selector_port import FileSelectorPort
from typing import Optional
import os
import json
from pathlib import Path

def _find_svg_files_recursively(directory: str):
    svg_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.svg'):
                svg_files.append(os.path.join(root, file))
    return svg_files

class SvgFileSelectorAdapter(FileSelectorPort):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../infrastructure/config/config.json')

    def _load_config(self):
        with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self, config):
        with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def select_svg_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        config = self._load_config()
        svg_input_dir = initial_dir or config.get('SVG_INPUT_DIR', './data/svg_input')
        while True:
            svg_files = _find_svg_files_recursively(svg_input_dir)
            if svg_files:
                print("Archivos SVG encontrados:")
                for idx, file in enumerate(svg_files, 1):
                    print(f"  [{idx}] {file}")
                print("  [0] Cancelar")
                try:
                    choice = int(input("Seleccione un archivo SVG por número: "))
                except ValueError:
                    print("Opción inválida.")
                    continue
                if choice == 0:
                    print("Operación cancelada por el usuario.")
                    return None
                if 1 <= choice <= len(svg_files):
                    return svg_files[choice - 1]
                print("Selección fuera de rango.")
            else:
                print(f"No se encontraron archivos SVG en '{svg_input_dir}'.")
                print("1) Asignar nueva carpeta de entrada")
                print("2) Reintentar (debe colocar un archivo SVG en la carpeta actual)")
                print("0) Cancelar")
                opt = input("Seleccione una opción: ").strip()
                if opt == '1':
                    new_dir = input("Ingrese la nueva ruta de carpeta para SVGs: ").strip()
                    if os.path.isdir(new_dir):
                        svg_input_dir = new_dir
                        config['SVG_INPUT_DIR'] = new_dir
                        self._save_config(config)
                        print(f"SVG_INPUT_DIR actualizado a: {new_dir}")
                    else:
                        print("Carpeta no válida.")
                elif opt == '2':
                    print("Por favor, coloque al menos un archivo SVG en la carpeta y presione Enter para reintentar.")
                    input()
                elif opt == '0':
                    print("Operación cancelada por el usuario.")
                    return None
                else:
                    print("Opción inválida.")
