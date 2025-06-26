"""
Módulo para gestionar argumentos de línea de comandos para simple_svg2gcode.
"""
import argparse
from pathlib import Path

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convierte archivos SVG en recorridos G-code para plotters o CNC sencillos.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 2.0.0")
    parser.add_argument("--no-interactive", action="store_true", help="Ejecutar en modo no interactivo")
    parser.add_argument("--no-color", action="store_true", help="Desactivar colores en la salida")
    parser.add_argument("--lang", choices=["es", "en"], default="es", help="Idioma de la interfaz (es, en)")
    parser.add_argument("-i", "--input", type=Path, help="Archivo SVG o G-code de entrada")
    parser.add_argument("-o", "--output", type=Path, help="Archivo G-code de salida")
    parser.add_argument("--optimize", action="store_true", help="Aplicar optimización de movimientos")
    parser.add_argument("--rescale", type=float, help="Factor de reescalado para el archivo G-code")
    parser.add_argument("--save-config", action="store_true", help="Guardar los argumentos actuales como configuración de usuario")
    parser.add_argument("--config", type=Path, help="Ruta a archivo de configuración personalizado (JSON)")
    return parser
