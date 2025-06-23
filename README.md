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

- `adapters/`: Adaptadores de entrada/salida (implementaciones de puertos definidos en dominio).
- `application/use_cases/`: Casos de uso y orquestación de lógica de negocio.
- `cli/main.py`: Punto de entrada principal para convertir SVG a G-code (nuevo flujo modularizado).
- `infrastructure/config/`: Configuración y parámetros del sistema (migrado desde `config/`).
- `infrastructure/storage/svg_input/`: Carpeta donde colocar los archivos SVG a procesar.
- `infrastructure/storage/gcode_output/`: Carpeta donde se guardan los archivos G-code generados.
- `domain/`: Entidades, modelos, lógica de negocio y puertos (interfaces).
- `domain/services/optimization/`: Optimizadores de G-code (lógica de negocio).
- `infrastructure/`: Implementaciones técnicas y utilidades.

## Uso

1. Coloca tus archivos `.svg` en la carpeta `infrastructure/storage/svg_input/`.
2. Desde la raíz del proyecto, ejecuta:

   ```powershell
   python run.py
   ```
   O en Linux/Mac:
   ```bash
   python run.py
   ```

3. Selecciona el archivo SVG a procesar cuando se te indique.
4. El archivo G-code generado aparecerá en la carpeta `infrastructure/storage/gcode_output/`.

## Ejecución recomendada

Para iniciar el proyecto, ejecuta siempre desde la raíz:

```powershell
python run.py
```

> **Nota:** No está habilitado ejecutar `python cli/main.py` ni `python -m cli.main` directamente. El punto de entrada oficial es `run.py`.

## Parámetros de configuración relevantes

- `REMOVE_SVG_BORDER` (bool): Si es `true`, intenta eliminar el marco/borde exterior del SVG si coincide exactamente con el `viewBox`.
- `BORDER_DETECTION_TOLERANCE` (float): Tolerancia relativa (por defecto 0.05) usada para comparar los márgenes del path con el `viewBox`. Un valor menor hace la detección más estricta; un valor mayor la hace más laxa. Si tienes rectángulos internos que no deben eliminarse, ajusta este valor para evitar falsos positivos.

---

### Notas de arquitectura (2025)
- Adaptadores consolidados en `adapters/`.
- Optimizadores movidos a `domain/services/optimization/`.
- Inyección de configuración en adaptadores.
- Eliminados tests y código legacy.
- Estructura y nomenclatura alineadas a Clean Architecture.
