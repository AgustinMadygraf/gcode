"""
Adaptador CLI para la selección de archivos SVG.
Implementa FileSelectorPort y permite al usuario elegir un archivo SVG desde la consola.
Guarda y recupera la carpeta de entrada desde un archivo de configuración JSON.
"""
import os

def _find_svg_files_recursively(directory: str):
    """Busca archivos SVG de forma recursiva en el directorio dado."""
    svg_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.svg'):
                svg_files.append(os.path.join(root, file))
    return svg_files

