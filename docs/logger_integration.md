# Guía de Integración del Logger

Esta guía describe cómo implementar y utilizar el sistema de logging desacoplado en el proyecto siguiendo Clean Architecture.

## 1. Principios
- **Nunca** importar ni usar un logger global.
- El logger debe inyectarse por parámetro en constructores o funciones.
- Usar siempre la interfaz `LoggerPort` definida en `domain/ports/logger_port.py`.
- Crear loggers usando `LoggerFactory` (`infrastructure/factories/logger_factory.py`).

## 2. Ejemplo de Creación de Logger
```python
from infrastructure.factories.logger_factory import LoggerFactory
logger = LoggerFactory.create_logger(
    context_name="my_component",
    use_color=True,
    level="DEBUG",
    show_file_line=True
)
```

## 3. Inyección en Componentes
```python
class MyAdapter:
    def __init__(self, logger, ...):
        self.logger = logger
    def do_something(self):
        self.logger.info("Mensaje informativo")
```

## 4. Uso en CLI
- El logger debe crearse en el punto de entrada y pasarse a todos los componentes.
- Ejemplo:
```python
logger = LoggerFactory.create_logger("cli", use_color=True, level="INFO")
presenter = CliPresenter(logger_instance=logger, ...)
```

## 5. Modo --dev
- Si el usuario pasa `--dev`, crear el logger con `level="DEBUG"` y `show_file_line=True`.

## 6. Ejemplo de Propagación
```python
# run.py
logger = LoggerFactory.create_logger("app", use_color=True, level="DEBUG")
app = SvgToGcodeApp(logger=logger)
app.run()
```

## 7. Prohibido
- No usar `from infrastructure.logger import logger`.
- No crear loggers ad-hoc fuera de la factory.

## 8. Testing
- Para tests, inyectar un mock o un logger de consola con nivel `DEBUG`.

---
Para más detalles, ver también `docs/logging.md` y ejemplos en la carpeta `cli/`.
