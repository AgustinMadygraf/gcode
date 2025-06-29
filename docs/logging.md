# Logging y modo desarrollador (`--dev`)

## Niveles y colores

| Nivel     | Prefijo     | Color ANSI   |
|-----------|-------------|-------------|
| `ERROR`   | `[ERROR]`   | Rojo         |
| `WARNING` | `[WARN]`    | Amarillo     |
| `INFO`    | `[INFO]`    | Verde        |
| `DEBUG`   | `[DEBUG]`   | Cian         |
| `INPUT`   | `[INPUT]`   | Azul         |

- El flag `--no-color` fuerza salida sin colores.
- El flag `--dev` o `--debug` activa nivel `DEBUG`, stacktrace extendido y agrega archivo:línea a cada mensaje `[INFO]` y `[DEBUG]`.

## Ejemplo de salida en consola (modo normal)
```
[INFO]   Archivo SVG cargado correctamente
[INPUT]  Selecciona el archivo a procesar:
[WARN]   El archivo ya existe, se sobrescribirá
[ERROR]  Validación de entrada: El archivo no es SVG válido
```

## Ejemplo de salida en consola (modo desarrollador `--dev`)
```
[INFO cli/main.py:42] Archivo SVG cargado correctamente
[DEBUG adapters/input/svg_loader_adapter.py:17] SVG parseado exitosamente
[ERROR] Validación de entrada: El archivo no es SVG válido
Traceback (most recent call last):
  ...
FileNotFoundError: ...
```

## Configuración avanzada

- El sistema crea un logger independiente para cada ejecución usando `InfraFactory.get_logger()`.
- El flag `--dev` activa nivel `DEBUG`, stacktrace extendido y archivo:línea en logs.
- Se recomienda evitar el uso del logger global y siempre inyectar el logger contextual.

## Ejemplo avanzado

```python
from infrastructure.factories.infra_factory import InfraFactory
logger = InfraFactory.get_logger(use_color=False, level='DEBUG', show_file_line=True)
```

## Recomendaciones
- No activar `--dev` por defecto en producción ni en CI.
- Documentar el uso de logs con archivo:línea en reportes de bugs.
