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
- `cli/main.py`: Contiene la lógica principal de la CLI, pero **no debe ejecutarse directamente**.
- `run.py`: **Único punto de entrada oficial**. Importa y ejecuta la aplicación desde `cli/main.py`.
- `infrastructure/config/`: Configuración y parámetros del sistema.
- `data/svg_input/`: Carpeta donde colocar los archivos SVG a procesar. (opcional, puedes usar cualquier ruta desde el CLI)
- `data/gcode_output/`: Carpeta donde se guardan los archivos G-code generados. (opcional, configurable)
- `domain/`: Entidades, modelos, lógica de negocio y puertos (interfaces).
- `docs/`: Documentación de arquitectura y cambios.
- `tests/`: Pruebas unitarias e integración.

## Uso

1. Coloca tus archivos `.svg` en la carpeta que desees (por defecto `data/svg_input/`).
2. Desde la raíz del proyecto, ejecuta:

   ```powershell
   python run.py
   ```
   O en Linux/Mac:
   ```bash
   python run.py
   ```

3. Selecciona el archivo SVG a procesar cuando se te indique.
4. El archivo G-code generado aparecerá en la carpeta configurada (por defecto `data/gcode_output/`).

> **Nota:** El punto de entrada oficial es `run.py`. No ejecutar directamente `cli/main.py`.
> Toda la lógica de orquestación reside en `cli/main.py`, pero solo debe ser invocada desde `run.py`.

## Ejecución recomendada

Para iniciar el proyecto, ejecuta siempre desde la raíz:

```powershell
python run.py
```

> **Nota:** No está habilitado ejecutar `python cli/main.py` ni `python -m cli.main` directamente. El punto de entrada oficial es `run.py`.
> Si necesitas extender la aplicación (por ejemplo, con una API), crea un nuevo entrypoint siguiendo este patrón.

## Parámetros de configuración relevantes

- `REMOVE_SVG_BORDER` (bool): Si es `true`, intenta eliminar el marco/borde exterior del SVG si coincide exactamente con el `viewBox`.
- `BORDER_DETECTION_TOLERANCE` (float): Tolerancia relativa (por defecto 0.05) usada para comparar los márgenes del path con el `viewBox`. Un valor menor hace la detección más estricta; un valor mayor la hace más laxa. Si tienes rectángulos internos que no deben eliminarse, ajusta este valor para evitar falsos positivos.

## Avanzado: Velocidad variable en curvas

Desde la versión 2025, el sistema ajusta automáticamente la velocidad (feed rate) en curvas para mejorar la calidad de línea y reducir el desgaste de la lapicera:

- `CURVATURE_ADJUSTMENT_FACTOR` (float): Controla cuánto se reduce la velocidad en curvas. Rango recomendado: 0.1 (sutil) a 0.4 (agresivo). Por defecto: 0.25
- `MINIMUM_FEED_FACTOR` (float): Límite inferior de velocidad como porcentaje del feed base. Rango típico: 0.3–0.7. Por defecto: 0.5

**Ejemplo de configuración en `infrastructure/config/config_curvature_sample.json`:**

```json
{
  "CURVATURE_ADJUSTMENT_FACTOR": 0.3,
  "MINIMUM_FEED_FACTOR": 0.5
}
```

**Recomendaciones para papel kraft:**
- Usa `CURVATURE_ADJUSTMENT_FACTOR=0.3` para lapiceras de tinta
- Usa `CURVATURE_ADJUSTMENT_FACTOR=0.2` para lápiz

El ajuste es automático y no requiere modificar el SVG ni el G-code manualmente.

---

## Uso interactivo

1. Coloca tus archivos `.svg` en la carpeta que desees (por defecto `data/svg_input/`).
2. Desde la raíz del proyecto, ejecuta:

   ```powershell
   python run.py
   ```
   O en Linux/Mac:
   ```bash
   python run.py
   ```
3. Selecciona el archivo SVG o GCODE y la operación cuando se te indique.
4. El archivo G-code generado aparecerá en la carpeta configurada (por defecto `data/gcode_output/`).

## Uso no interactivo (batch/script)

Puedes automatizar la conversión y optimización usando argumentos:

- `--input` (`-i`): Archivo de entrada (SVG o GCODE)
- `--output` (`-o`): Archivo de salida (opcional)
- `--optimize`: Optimiza movimientos G1→G0 en GCODE
- `--rescale <factor>`: Reescala GCODE por el factor indicado (ej: 1.5)
- `--lang <es|en>`: Idioma de los mensajes
- `--no-color`: Desactiva colores en la terminal
- `--no-interactive`: Ejecuta sin menús ni prompts
- `--save-config`: Guarda los argumentos actuales como preferencias de usuario persistentes.
- `--config <ruta>`: Usa un archivo de configuración personalizado (JSON).

### Ejemplos

**Convertir SVG a GCODE (no interactivo):**
```powershell
python run.py --no-interactive --input dibujo.svg --output resultado.gcode
```

**Optimizar movimientos en un GCODE existente:**
```powershell
python run.py --no-interactive --input archivo.gcode --optimize
```

**Reescalar un GCODE existente:**
```powershell
python run.py --no-interactive --input archivo.gcode --rescale 1.5
```

**Mostrar ayuda y opciones:**
```powershell
python run.py --help
```

### Ejemplos con redirección y pipes

**Convertir SVG desde stdin y escribir G-code a stdout:**
```bash
cat dibujo.svg | python run.py --no-interactive --input - --output - > resultado.gcode
```

**Optimizar un G-code usando redirección:**
```bash
python run.py --no-interactive --input archivo.gcode --optimize --output - > optimizado.gcode
```

**Usar en un pipeline (SVG → G-code → optimización):**
```bash
cat dibujo.svg | python run.py --no-interactive --input - --output - | \
  python run.py --no-interactive --input - --optimize --output resultado.gcode
```

> Todos los mensajes y errores respetan el idioma y colores configurados.

## Idioma automático

Por defecto, la aplicación detecta el idioma del sistema operativo:
- Si tu sistema está en inglés, la interfaz será en inglés.
- En cualquier otro caso, la interfaz será en español.
- Puedes forzar el idioma con el flag `--lang es` o `--lang en`.

### Notas de arquitectura (2025)
- Adaptadores consolidados en `adapters/`.
- Optimizadores movidos a `domain/services/optimization/`.
- Inyección de configuración en adaptadores.
- Eliminados tests y código legacy.
- Estructura y nomenclatura alineadas a Clean Architecture.

## Solución de problemas (Troubleshooting)

### El comando `python run.py` no hace nada o muestra error de importación
- Asegúrate de estar en la raíz del proyecto y de tener Python 3.8+ instalado.
- Verifica que ejecutas `python run.py` y **no** `cli/main.py` directamente.

### Mensaje: `[ERROR] Archivo no encontrado`
- Revisa la ruta y nombre del archivo pasado con `--input`.
- Si usas modo interactivo, asegúrate de seleccionar un archivo válido.

### Mensaje: `Permission denied` o problemas de escritura
- Verifica permisos de escritura en la carpeta de salida (`data/gcode_output/` o la que configures).
- En Windows, ejecuta la terminal como administrador si es necesario.

### Los colores no se ven bien en mi terminal
- Usa el flag `--no-color` para desactivar colores ANSI.
- En Windows, algunos terminales antiguos no soportan colores.

### Los mensajes aparecen en español pero quiero inglés
- Usa el flag `--lang en` para mostrar los mensajes en inglés.

### No se genera el archivo de salida esperado
- Si no especificas `--output`, el sistema genera un nombre automáticamente en la carpeta de salida.
- Revisa los logs o mensajes de error para más detalles.

### ¿Cómo reporto un bug?
- Abre un issue en el repositorio o contacta al mantenedor con el mensaje de error y los pasos para reproducirlo.

## Códigos de salida

La aplicación retorna diferentes códigos de salida según el resultado de la ejecución. Úsalos para automatizar flujos o detectar errores en scripts:

| Código | Significado                        |
|--------|------------------------------------|
| 0      | Ejecución exitosa                  |
| 1      | Error general de aplicación        |
| 2      | Error de validación de entrada     |
| 3      | Error durante el procesamiento     |
| 4      | Error en la generación de salida   |
| 99     | Error inesperado/desconocido       |

> Los mensajes de error se muestran en el idioma configurado y con prefijos `[ERROR]`.

## Selección de herramienta

La aplicación permite elegir entre dos tipos de herramientas:

- **Lapicera (`--tool pen`)**: Para trazado preciso de contornos
  - Opción de doble pasada (`--double-pass`) para mejorar definición

- **Fibrón grueso (`--tool marker`)**: Para rellenos o contornos sin repetición
  - Usa una velocidad reducida automáticamente para mejor deposición de tinta

### Ejemplos

```bash
# Usar lapicera con doble pasada
python run.py --tool pen --double-pass

# Usar fibrón grueso
python run.py --tool marker
```
