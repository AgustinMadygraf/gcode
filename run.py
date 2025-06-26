"""
Path: run.py

Punto de entrada oficial de la aplicación (Clean Architecture).
Procesa argumentos CLI y los pasa a la aplicación.
"""

from cli.argument_parser import create_parser
from cli.main import SvgToGcodeApp

def main():
    parser = create_parser()
    args = parser.parse_args()
    app = SvgToGcodeApp(args)
    return app.run()

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
