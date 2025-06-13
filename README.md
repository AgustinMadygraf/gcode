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
- `run.py`: Script principal para convertir SVG a G-code.
- `svg_input/`: Carpeta donde colocar los archivos SVG a procesar.
- `gcode_output/`: Carpeta donde se guardan los archivos G-code generados.

## Uso

1. Coloca tus archivos `.svg` en la carpeta `svg_input`.
2. Ejecuta el script principal:

   ```bash
   python run.py
   ```

3. Selecciona el archivo SVG a procesar cuando se te indique.
4. El archivo G-code generado aparecerá en la carpeta `gcode_output`.

---
