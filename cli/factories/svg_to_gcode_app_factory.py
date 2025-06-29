"""
Factory para construir la aplicación SvgToGcodeApp con todas sus dependencias.
"""
from cli.main import SvgToGcodeApp

def create_svg_to_gcode_app(args=None, logger=None):
    """
    Construye y retorna una instancia de SvgToGcodeApp con todas las dependencias configuradas.
    """
    return SvgToGcodeApp(args, logger=logger)
