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

> **Nota:** El menú principal de la aplicación siempre muestra las mismas opciones principales:
>  1. Convertir SVG → G-code
>  2. Optimizar G-code (submenú)
>  0. Salir
> Estas opciones son fijas salvo que se extienda la aplicación mediante plugins o desarrollo avanzado.

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
- `--dev`, `--debug`: Activa modo desarrollador (logging DEBUG, stacktrace extendido)
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

## Documentación avanzada

- [Arquitectura y capas](docs/architecture.md)
- [Logging y modo desarrollador](docs/logging.md)
- [Solución de problemas (Troubleshooting)](docs/troubleshooting.md)
- [Ejemplos y uso avanzado](docs/usage_advanced.md)

## Logging, colores y niveles

> Para detalles avanzados de logging, formato `[INFO archivo:línea]` y modo `--dev`, consulta [docs/logging.md](docs/logging.md).

Todos los mensajes de la aplicación usan un sistema de logging centralizado con los siguientes niveles y colores ANSI (desactivables con `--no-color`):

| Nivel     | Prefijo     | Color ANSI   |
|-----------|-------------|-------------|
| `ERROR`   | `[ERROR]`   | Rojo         |
| `WARNING` | `[WARN]`    | Amarillo     |
| `INFO`    | `[INFO]`    | Verde        |
| `DEBUG`   | `[DEBUG]`   | Cian         |
| `INPUT`   | `[INPUT]`   | Azul         |

- El flag `--no-color` fuerza salida sin colores (accesible para lectores de pantalla o logs).
- El flag `--dev` o `--debug` activa nivel `DEBUG`, muestra stacktrace extendido y agrega archivo:línea a cada mensaje `[INFO]` y `[DEBUG]`.
- Todos los mensajes de input interactivo usan el prefijo `[INPUT]`.

**Ejemplo de salida en consola (modo normal):**
```
[INFO]   Archivo SVG cargado correctamente
[INPUT]  Selecciona el archivo a procesar:
[WARN]   El archivo ya existe, se sobrescribirá
[ERROR]  Validación de entrada: El archivo no es SVG válido
```

**Ejemplo de salida en consola (modo desarrollador `--dev`):**
```
[INFO cli/main.py:42] Archivo SVG cargado correctamente
[DEBUG adapters/input/svg_loader_adapter.py:17] SVG parseado exitosamente
[ERROR] Validación de entrada: El archivo no es SVG válido
Traceback (most recent call last):
  ...
FileNotFoundError: ...
```

## Modo desarrollador (`--dev`)

> Para ejemplos y explicación completa del modo desarrollador, consulta [docs/logging.md](docs/logging.md).

Puedes activar el modo desarrollador para obtener logs detallados (nivel DEBUG), stacktrace extendido y trazabilidad de archivo:línea en cada mensaje `[INFO]` y `[DEBUG]`:

```bash
python run.py --dev --input archivo_invalido.svg
```

- Si ocurre un error, verás información de depuración y el stacktrace completo.
- Sin `--dev`, solo se muestra un mensaje de error amigable.
- En modo `--dev`, cada mensaje `[INFO]` y `[DEBUG]` incluye el archivo y línea de origen.

**Ejemplo de salida con `--dev`:**
```
[DEBUG run.py:18] [DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.
[INFO adapters/input/svg_loader_adapter.py:17] Archivo SVG cargado correctamente
[ERROR] Validación de entrada: Archivo no encontrado: archivo_invalido.svg
Traceback (most recent call last):
  ...
FileNotFoundError: ...
```

**Ejemplo de salida sin `--dev`:**
```
[ERROR] Validación de entrada: Archivo no encontrado: archivo_invalido.svg
```

Este flag es útil para desarrollo, debugging y reporte de errores detallados.

## Troubleshooting

> Para solución de problemas y preguntas frecuentes, consulta [docs/troubleshooting.md](docs/troubleshooting.md).

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

## Ejecución avanzada

> Para ejemplos de uso batch, pipes y configuración avanzada, consulta [docs/usage_advanced.md](docs/usage_advanced.md).

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

## Colores en la terminal

La aplicación detecta automáticamente si la terminal soporta colores ANSI. Si no es compatible, los mensajes se mostrarán sin color.

- Para forzar la salida sin color, usa el flag `--no-color`.
- En Windows, los colores funcionan en terminales modernas (PowerShell, Windows Terminal, VSCode). En CMD clásico pueden no verse.
- En scripts o pipes, los colores se desactivan automáticamente.

**Ejemplo:**
```bash
python run.py --no-color --input ejemplo.svg --output salida.gcode
```

> **Advertencia:** Si ves caracteres extraños como `[91m`, tu terminal no soporta colores ANSI. Usa `--no-color`.

## Optimización y compresión automática de G-code

A partir de la versión 2025, la optimización de trayectorias y la compresión inteligente de comandos G-code están **siempre activas**. No es necesario usar flags ni opciones especiales: todos los archivos generados pasan automáticamente por un proceso de optimización y compresión que incluye:

- Reordenamiento global de trayectorias para minimizar movimientos en vacío.
- Compresión avanzada de comandos (reducción de redundancias, uso de arcos y líneas optimizadas, alternancia entre modos absoluto/relativo si es seguro).
- Minimización de movimientos no productivos.

Esto garantiza archivos más pequeños, recorridos más eficientes y menor desgaste mecánico, sin intervención manual.

> Si necesitas desactivar la optimización por motivos de debugging avanzado, consulta la documentación técnica para opciones internas.

## Convención de logging: logger directo vs presentador

- **Mensajes de sistema** (inicio, errores globales, stacktrace): usar el logger directamente. Ejemplo:
  ```python
  logger.debug("[DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.")
  ```
  Salida:
  ```
  [DEBUG run.py:23] [DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.
  ```
- **Mensajes de usuario/interacción**: usar siempre el presentador o adapters, que pasan el logger con stacklevel adecuado. Ejemplo:
  ```python
  presenter.print("Menú Principal")
  ```
  Salida:
  ```
  [INFO orchestrator.py:73] Menú Principal
  ```

Esto asegura que los logs de usuario siempre muestran el archivo/línea del llamador real, y los de sistema muestran el entrypoint.
