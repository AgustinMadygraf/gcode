"""
Módulo para gestionar argumentos de línea de comandos para simple_svg2gcode.
"""
import argparse
from pathlib import Path
from cli.i18n import get_message
from infrastructure.config.config import Config

def create_parser() -> argparse.ArgumentParser:
    " Crea y configura el ArgumentParser para la CLI. "
    config = Config()
    presets = config.get("SURFACE_PRESETS", {})
    preset_names = list(presets.keys())
    preset_help = (
        get_message('ARG_SURFACE_PRESET') +
        "\nPresets disponibles: " + ', '.join(preset_names)
        if preset_names else get_message('ARG_SURFACE_PRESET')
    )
    parser = argparse.ArgumentParser(
        description=get_message('ARGPARSE_DESCRIPTION'),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 2.0.0")
    parser.add_argument("--no-interactive", action="store_true", help=get_message('ARG_NO_INTERACTIVE'))
    parser.add_argument("--no-color", action="store_true", help=get_message('ARG_NO_COLOR'))
    parser.add_argument("--lang", choices=["es", "en"], default="es", help=get_message('ARG_LANG'))
    parser.add_argument("-i", "--input", type=str, help=get_message('ARG_INPUT'))
    parser.add_argument("-o", "--output", type=str, help=get_message('ARG_OUTPUT'))
    parser.add_argument("--optimize", action="store_true", help=get_message('ARG_OPTIMIZE'))
    parser.add_argument("--rescale", type=float, help=get_message('ARG_RESCALE'))
    parser.add_argument("--save-config", action="store_true", help=get_message('ARG_SAVE_CONFIG'))
    parser.add_argument("--config", type=Path, help=get_message('ARG_CONFIG'))
    parser.add_argument("--tool", choices=["pen", "marker"], default="pen",
                        help=get_message('ARG_TOOL'))
    parser.add_argument("--double-pass", action="store_true", default=None,
                        help=get_message('ARG_DOUBLE_PASS'))
    parser.add_argument("--no-double-pass", dest="double_pass", action="store_false",
                        help=get_message('ARG_NO_DOUBLE_PASS'))
    parser.add_argument(
        "--tool-diameter",
        type=float,
        default=None,
        help="Diámetro de la herramienta en mm (sobrescribe configuración)"
    )
    parser.add_argument(
        "--dev", "--debug", action="store_true",
        help=get_message('ARG_DEV')
    )
    parser.add_argument(
        "--surface-preset",
        type=str,
        help=preset_help
    )
    parser.add_argument(
        "--offset-x",
        type=float,
        default=None,
        help="Offset horizontal en mm (desplazamiento X del dibujo en el área útil)"
    )
    parser.add_argument(
        "--offset-y",
        type=float,
        default=None,
        help="Offset vertical en mm (desplazamiento Y del dibujo en el área útil)"
    )
    parser.add_argument(
        "--center",
        action="store_true",
        help="Centrar automáticamente el dibujo en el área útil"
    )
    return parser
