# Arquitectura del Proyecto GCode

## Introducción
Este documento describe la arquitectura del proyecto GCode, basada en los principios de Clean Architecture. El objetivo es mantener una separación clara de responsabilidades, facilitar la escalabilidad y asegurar la mantenibilidad del código.

## Mapa de Capas
```
gcode/
├── adapters/                  # Adaptadores de entrada/salida (implementaciones de puertos)
├── application/
│   └── use_cases/            # Casos de uso y orquestación
│       └── path_processing/  # Orquestación de conversión de paths a G-code
├── cli/                      # Interfaz de usuario (CLI)
├── infrastructure/
│   └── config/               # Configuración (migrada desde config/)
├── domain/                   # Entidades, modelos, lógica de negocio, puertos
│   └── ports/                # Puertos (interfaces) de dominio
│   └── services/
│       └── optimization/     # Optimizadores de G-code (lógica de negocio)
├── data/svg_input/           # Archivos SVG de entrada
├── data/gcode_output/        # Archivos G-code generados
├── tests/                    # Tests unitarios y de integración
└── docs/                     # Documentación
```

## Cambios recientes (06/2025)
- Refactorización modular de `GCodeGeneratorAdapter`:
    - Lógica de ajuste de velocidad/curvatura extraída a `adapters/output/feed_rate_strategy.py`.
    - Pipeline de muestreo y transformación extraído a `adapters/output/sample_transform_pipeline.py`.
    - Lógica de construcción de comandos G-code extraída a `adapters/output/gcode_builder_helper.py`.
    - Métodos y dependencias desacoplados para facilitar extensión y pruebas.
- Implementado lazy loading de dependencias en `infrastructure/factories/container.py`.
- `FilenameService` migrado de `application/use_cases/file_output` a `domain/services/filename_service.py`.
- Caso de uso orquestador `SvgToGcodeUseCase` en `application/use_cases/svg_to_gcode_use_case.py`.
- Suite de tests robusta y alineada a la arquitectura actual.
- Adaptadores consolidados en `adapters/`.
- Optimizadores movidos a `domain/services/optimization/`.
- Inyección de configuración en adaptadores (usando `infrastructure.config.Config`).
- Eliminados tests y código legacy.
- Orquestación de conversión de paths a G-code integrada en `application/use_cases/path_processing/path_processing_service.py`.
- Archivo `domain/path_conversion_service.py` eliminado definitivamente (junio 2025).
- Archivo `domain/ports/path_conversion_port.py` eliminado por ser código muerto (junio 2025).
- Estructura y nomenclatura alineadas a Clean Architecture.

## Descripción de Capas

### 1. Dominio (`domain/`)
- Contiene entidades, modelos, lógica de negocio y puertos (interfaces).
- No depende de ninguna otra capa.

### 2. Aplicación (`application/`)
- Orquesta casos de uso y coordina servicios de dominio.
- Depende solo de la capa de dominio.
- La orquestación de conversión de paths a G-code reside aquí.

### 3. Infraestructura (`infrastructure/`, `infrastructure/config/`)
- Implementa adaptadores, servicios externos y detalles técnicos.
- Depende de dominio y aplicación, nunca al revés.

### 4. Interfaz (`cli/`)
- Provee la interfaz de usuario (CLI).
- Puede interactuar con aplicación e infraestructura.

## Reglas de Dependencia
- Las dependencias siempre apuntan hacia el dominio.
- La infraestructura y la interfaz nunca deben ser importadas por dominio o aplicación.
- Los puertos (interfaces) se definen en dominio y se implementan en infraestructura/adapters.

## Patrón de Dependencias Correcto

- Los puertos (interfaces) del dominio (`domain/ports/`) nunca importan adaptadores, infraestructura ni aplicación.
- Los adaptadores (`adapters/`) implementan los puertos y dependen de ellos, nunca al revés.
- No existen ciclos de importación entre capas.
- Si se detecta una dependencia cruzada, aplicar inversión de dependencias (crear interfaz en dominio y mover implementación a adaptadores/infrastructure).

Este patrón asegura la independencia y testabilidad del dominio, y previene acoplamientos indebidos.

## Principios Clave
- **Inversión de dependencias:** El dominio define interfaces, la infraestructura/adapters las implementa.
- **Separación de responsabilidades:** Cada capa tiene un propósito claro.
- **DRY:** Evitar duplicidad de lógica entre capas.

## Diagrama Simplificado

```
[ CLI ]
   |
[ Application ]
   |
[ Domain ] <--- [ Infrastructure ]
```

## Flujo de inicio

1. El usuario ejecuta `python run.py` desde la raíz del proyecto.
2. `run.py` importa y crea una instancia de `SvgToGcodeApp` desde `cli/main.py`.
3. `SvgToGcodeApp` delega la orquestación principal a `ApplicationOrchestrator` (`application/orchestrator.py`).
4. La gestión de eventos desacoplada se realiza mediante `EventManager` (`infrastructure/events/event_manager.py`).
5. Toda la lógica de ciclo de vida de la app reside en el orquestador y workflows.
6. Si se requiere otro entrypoint (API, GUI), debe crearse un archivo similar a `run.py`.

> **Nota:** Solo `run.py` debe usarse como punto de entrada. No ejecutar directamente `cli/main.py`.

## Patrón de eventos (Event Manager)

- El dominio define el puerto `EventBusPort` para publicar y suscribirse a eventos.
- La infraestructura implementa el gestor de eventos (`EventManager`).
- El contenedor inyecta el gestor de eventos y lo expone como dependencia transversal.
- Los casos de uso y la CLI pueden publicar eventos (por ejemplo, `GcodeGeneratedEvent`) y suscribirse a ellos para acciones secundarias (notificaciones, logs, auditoría, etc.).
- Este patrón permite desacoplar la lógica principal de acciones reactivas y facilita la extensión futura.

### Ejemplo de uso

```python
# Publicar evento tras generar G-code
from infrastructure.events.event_manager import EventManager
from domain.events.events import GcodeGeneratedEvent

event_manager = EventManager()
event_manager.publish(GcodeGeneratedEvent(...))

# Suscribirse a evento
event_manager.subscribe(GcodeGeneratedEvent, handler_func)
```

## Logger y riesgos de logger global

El sistema soporta la creación de loggers por contexto/app usando `InfraFactory.get_logger()`, permitiendo configurar nivel, color y destino de logs para cada ejecución.

> **Advertencia:** Ya NO existe ninguna instancia global de logger en el sistema. El uso de loggers debe ser siempre explícito y por inyección de dependencias. Cualquier intento de acceder a un logger global está prohibido y será considerado un error de arquitectura.

**Recomendaciones:**
- Usar siempre `InfraFactory.get_logger()` para obtener loggers configurados por contexto.
- Inyectar el logger en presenters, contenedores, casos de uso y cualquier componente que lo requiera.
- Documentar y testear el comportamiento esperado en modo `--dev` y en flujos concurrentes.
- Revisar periódicamente el código para asegurar que no se reintroducen instancias globales de logger.

## Logger, modo desarrollador y trazabilidad

El logger centralizado soporta el flag `--dev` (o `--debug`), que activa:
- Nivel de logging `DEBUG`.
- Stacktrace extendido en caso de error.
- Inclusión automática de archivo y línea de origen en cada mensaje `[INFO]` y `[DEBUG]`.

**Ejemplo de log en modo desarrollador:**
```
[INFO adapters/input/svg_loader_adapter.py:17] Archivo SVG cargado correctamente
[DEBUG run.py:18] [DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.
[ERROR] Validación de entrada: Archivo no encontrado: archivo_invalido.svg
Traceback (most recent call last):
  ...
FileNotFoundError: ...
```

Esto permite depuración precisa y reporte de errores reproducibles.

**Recomendaciones:**
- Usar siempre `InfraFactory.get_logger()` y propagar el flag `show_file_line` según el modo.
- No activar `--dev` por defecto en producción ni en CI.
- Documentar el uso de logs con archivo:línea en reportes de bugs.

## Inyección de logger en dominio y aplicación

Para asegurar la trazabilidad y desacoplamiento, el logger nunca se instancia directamente en el dominio. En su lugar, se inyecta desde infraestructura usando la factory global:

```python
from infrastructure.factories.infra_factory import InfraFactory
logger = InfraFactory.get_logger(name="app.path_processing", level="DEBUG", show_file_line=True)
path_filter = PathFilter(logger=logger)
svg_border_detector = SvgBorderDetector(logger=logger)
```

- Todos los servicios de dominio que requieren logging deben aceptar un parámetro `logger` en su constructor.
- La configuración global del logger (nivel, colores, formato, archivo:línea) se define en la infraestructura y se propaga a todos los componentes.
- El dominio nunca debe importar ni depender de `logging` ni de infraestructura, solo aceptar el logger como argumento.

### Ejemplo de logs de dominio en consola

```
[INFO domain/filters/svg_border_detector.py:42] Path es un rectángulo cerrado
[DEBUG domain/services/path_filter_service.py:27] Path 0: descartado por longitud (0.0000)
```

Este patrón permite testear y mockear el logger en pruebas, y asegura que todos los logs sigan el formato global.

## Notas y Recomendaciones
- Mantener la documentación de modelos e invariantes en `docs/domain_models.md`.
- Documentar cambios relevantes en `docs/CHANGELOG.md`.
- Revisar periódicamente dependencias para evitar inversiones indebidas.

---

_Última actualización: 23/06/2025_
