"""
path: tools/find_unused_references.py
"""

import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class VultureRunner:
    " Clase para ejecutar Vulture y generar un reporte de código muerto. "
    def __init__(self, folder, exclude, report_path):
        self.folder = folder
        self.exclude = exclude
        self.report_path = report_path

    def run(self):
        " Ejecuta Vulture en la carpeta especificada y guarda el reporte. "
        cmd = [
            sys.executable, "-m", "vulture", self.folder, "--exclude", self.exclude
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = result.stdout
        if result.returncode not in (0, 1, 3):
            print("Error ejecutando Vulture:")
            print(f"Comando ejecutado: {' '.join(cmd)}")
            print(f"Código de salida: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            sys.exit(result.returncode)
        rel_output = output.replace(
            PROJECT_ROOT + os.sep, ""
        ).replace(
            PROJECT_ROOT.replace("\\", "/") + "/", ""
        )
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(rel_output)
