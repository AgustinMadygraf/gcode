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

# Eliminado: SvgFileSelectorAdapter (movido a adapters/input/svg_file_selector_adapter.py)
