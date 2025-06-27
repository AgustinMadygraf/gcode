"""
Módulo auxiliar para manejo de entrada en workflows no interactivos.
Encapsula la lógica de selección y lectura de entrada (stdin, archivo, tipo SVG/GCODE).
"""

from pathlib import Path
import sys
from typing import Optional, Tuple

class InputHandler:
    def __init__(self, presenter):
        self.presenter = presenter

    def read(self, args) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Devuelve una tupla (input_type, input_data, temp_path)
        - input_type: 'svg', 'gcode' o None
        - input_data: contenido leído (si es stdin), None si es archivo
        - temp_path: ruta temporal si corresponde
        """
        input_path = args.input
        if not input_path:
            self.presenter.print("error_file_not_found", color='red')
            return None, None, None
        if input_path == '-':
            input_data = sys.stdin.read()
            # Detectar tipo por flags o extensión
            if getattr(args, 'optimize', False) or getattr(args, 'rescale', None) or (args.input and str(args.input).lower().endswith('.gcode')):
                return 'gcode', input_data, None
            else:
                return 'svg', input_data, None
        else:
            if str(input_path).lower().endswith('.svg'):
                return 'svg', None, input_path
            elif str(input_path).lower().endswith('.gcode'):
                return 'gcode', None, input_path
            else:
                self.presenter.print("error_occurred", color='red')
                return None, None, None
