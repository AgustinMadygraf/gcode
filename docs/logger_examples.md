# Plantillas de Ejemplo: Integración de Logger

## 1. Adaptador de Entrada
```python
from infrastructure.factories.logger_factory import LoggerFactory
from adapters.input.svg_file_selector_adapter import SvgFileSelectorAdapter

logger = LoggerFactory.create_logger("svg_file_selector", use_color=True, level="INFO")
adapter = SvgFileSelectorAdapter(logger=logger, i18n=i18n)
```

## 2. Caso de Uso
```python
from infrastructure.factories.logger_factory import LoggerFactory
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase

logger = LoggerFactory.create_logger("svg_to_gcode_use_case", level="DEBUG")
use_case = SvgToGcodeUseCase(logger=logger, ...)
```

## 3. Presentador CLI
```python
from infrastructure.factories.logger_factory import LoggerFactory
from cli.presenters.cli_presenter import CliPresenter

logger = LoggerFactory.create_logger("cli_presenter", use_color=True)
presenter = CliPresenter(logger_instance=logger, ...)
```

## 4. Servicio de Dominio (para testing)
```python
from infrastructure.factories.logger_factory import LoggerFactory
from domain.services.optimization.path_planner_optimizer import PathPlannerOptimizer

logger = LoggerFactory.create_logger("test.path_planner_optimizer", level="DEBUG")
optimizer = PathPlannerOptimizer(logger=logger)
```

## 5. Logger en Modo Dev
```python
from infrastructure.factories.logger_factory import LoggerFactory
logger = LoggerFactory.create_logger("app", use_color=True, level="DEBUG", show_file_line=True)
```

## 6. Logger en Tests
```python
import pytest
from infrastructure.factories.logger_factory import LoggerFactory

def test_logging_behavior():
    logger = LoggerFactory.create_logger("test", level="DEBUG")
    # Inyectar logger en el componente a testear
    ...
```

---
Para más ejemplos, ver `docs/logger_integration.md` y `docs/logging.md`.
