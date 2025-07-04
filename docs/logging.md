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

## Ejemplo recomendado de creación de logger

```python
from infrastructure.factories.logger_factory import LoggerFactory
logger = LoggerFactory.create_logger(
    context_name="my_component",
    use_color=True,
    level="DEBUG",
    show_file_line=True
)
```

## Prohibido

- No usar `from infrastructure.logger import logger`.
- No crear loggers ad-hoc fuera de la factory.

## Referencia

- Ver también: `docs/logger_integration.md` para una guía paso a paso y ejemplos de integración.

## Ejemplo avanzado

```python
from infrastructure.factories.infra_factory import InfraFactory
logger = InfraFactory.get_logger(use_color=False, level='DEBUG', show_file_line=True)
```

## Inyección de logger en dominio

- El dominio nunca debe crear loggers internos ni depender de `logging`.
- Siempre se debe inyectar el logger desde infraestructura usando `InfraFactory.get_logger()`.
- Ejemplo de uso en tests y servicios:

```python
from infrastructure.factories.infra_factory import InfraFactory
logger = InfraFactory.get_logger(name="test.svg_border_detector", level="DEBUG")
detector = SvgBorderDetector(logger=logger)
```

- La configuración global (nivel, colores, formato) se propaga a todos los loggers inyectados.
- Esto permite capturar y testear los logs de dominio en pruebas unitarias.

## Ejemplo de logs de dominio

```
[DEBUG domain/filters/svg_border_detector.py:27] No es rectángulo: segmentos=3
[INFO domain/services/path_filter_service.py:42] Total de paths eliminados como borde SVG: 1
```

## Ejemplo de test de logging con pytest y caplog

```python
import logging
import pytest
from domain.services.optimization.path_planner_optimizer import PathPlannerOptimizer
from domain.gcode.commands.move_command import MoveCommand

def test_logging_info_emitted_on_optimize(caplog):
    logger = logging.getLogger("test_logger")
    trazo1 = [MoveCommand(0, 0, rapid=True), MoveCommand(10, 0, feed=1000, rapid=False)]
    trazo2 = [MoveCommand(50, 50, rapid=True), MoveCommand(52, 50, feed=1000, rapid=False)]
    commands = trazo1 + trazo2
    optimizer = PathPlannerOptimizer()
    with caplog.at_level("INFO", logger="test_logger"):
        optimizer.optimize(commands, logger=logger)
    assert any("Orden final de trazos" in r.getMessage() for r in caplog.records)
```

- Usar `caplog` permite asertar sobre mensajes y niveles de log en tests automatizados.
- Se recomienda incluir tests de logs críticos y de formato (archivo:línea en modo dev).

## Estado de pruebas de logging

- El sistema de logging está completamente testeado con pruebas unitarias y de integración.
- Se verifica la emisión de logs en casos de éxito, error y en modo desarrollador (`archivo:línea`).
- Ejemplo de resultado esperado:

```
[DEBUG run.py:23] [DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.
[INFO path_planner_optimizer.py:132] Orden final de trazos (puntos de inicio): [(0, 0), (10, 0), (50, 50)]
[INFO path_planner_optimizer.py:133] Métricas de optimización: {'paths_reordered': 2, 'strategy': 'length+proximity-dynamic'}
[ERROR] Error al optimizar: Entrada inválida
```

- Se recomienda mantener y extender los tests de logging ante cambios futuros en la arquitectura o el formato de logs.

## Estado de migración de logging (julio 2025)

- Todo el código de producción utiliza exclusivamente el sistema de logging inyectado.
- No existen `print()` residuales en servicios, adaptadores ni casos de uso.
- Todos los mensajes relevantes (proceso, debugging, métricas, errores) son testeables y aparecen formateados en consola.
- La experiencia CLI es coherente y profesional, tanto en modo normal como en modo desarrollador (`--dev`).
- Se recomienda mantener este estándar en futuras contribuciones y revisar periódicamente con tests y auditorías.

## Recomendaciones
- No activar `--dev` por defecto en producción ni en CI.
- Documentar el uso de logs con archivo:línea en reportes de bugs.
