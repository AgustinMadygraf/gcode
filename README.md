# simple_svg2gcode

Convierte archivos SVG en recorridos G-code para plotters o CNC sencillos.

## Requisitos

- Python 3.8+
- [svgpathtools](https://pypi.org/project/svgpathtools/)
- [numpy](https://pypi.org/project/numpy/)

Instala dependencias con:

```bash
pip install svgpathtools numpy
```

## Estructura

- `src/svg_loader.py`: Clase para cargar y analizar archivos SVG.
- `cli/main.py`: Punto de entrada principal para convertir SVG a G-code (nuevo flujo modularizado).
- `domain/gcode_generator.py`: Lógica de conversión SVG → G-code.
- `infrastructure/`: Configuración y logging.
- `svg_input/`: Carpeta donde colocar los archivos SVG a procesar.
- `gcode_output/`: Carpeta donde se guardan los archivos G-code generados.

## Uso

1. Coloca tus archivos `.svg` en la carpeta `svg_input`.
2. Desde la raíz del proyecto, ejecuta:

   ```powershell
   $env:PYTHONPATH="."; python -m cli.main
   ```
   O en Linux/Mac:
   ```bash
   PYTHONPATH=. python -m cli.main
   ```

3. Selecciona el archivo SVG a procesar cuando se te indique.
4. El archivo G-code generado aparecerá en la carpeta `gcode_output`.

---
