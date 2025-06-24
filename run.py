"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
No contiene lógica de orquestación, solo inicia la app.
"""

from cli.main import SvgToGcodeApp

if __name__ == "__main__":
    app = SvgToGcodeApp()
    app.run()
