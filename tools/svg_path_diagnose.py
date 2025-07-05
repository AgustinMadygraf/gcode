"""
Path: tools/svg_path_diagnose.py
Diagnostica y muestra información sobre los paths en un archivo SVG.
"""
import sys
from svgpathtools import svg2paths2

if len(sys.argv) < 2:
    print("Uso: python svg_path_diagnose.py <archivo_svg>")
    sys.exit(1)

svg_file = sys.argv[1]
try:
    paths, attributes, svg_attributes = svg2paths2(svg_file)
    print(f"Archivo: {svg_file}")
    print(f"Cantidad de paths encontrados: {len(paths)}")
    for i, (p, attr) in enumerate(zip(paths, attributes)):
        print(f"\nPath #{i+1}:")
        print(f"  d: {attr.get('d', '')[:120]}{'...' if len(attr.get('d',''))>120 else ''}")
        print(f"  Atributos: {attr}")
    if not paths:
        print("No se encontraron paths. El parser no pudo extraerlos.")
except FileNotFoundError as e:
    print(f"Archivo no encontrado: {e}")
except OSError as e:
    print(f"Error de sistema al leer el archivo: {e}")
except ValueError as e:
    print(f"Error de valor al procesar el SVG: {e}")
