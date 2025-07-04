# Testing del Sistema de Logging

## 1. Pruebas Unitarias del Logger
- Se testean colores, niveles y formato en `tests/unit_tests/test_logger.py`.
- Ejemplo:
```python
from infrastructure.logger import ConsoleLogger

def test_logger_info_colored():
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=True, stream=buf, level='INFO')
    logger.info('Mensaje info')
    output = buf.getvalue()
    assert '[INFO]' in output
    assert '\x1b[32m' in output  # Verde
```

## 2. Pruebas de Propagación y Formato Dev
- Se verifica que el logger en modo dev incluya archivo:línea y stacktrace.
- Ejemplo:
```python
# tests/unit_tests/test_path_planner_optimizer_logging_dev.py
with caplog.at_level("INFO", logger="test_logger_dev"):
    optimizer.optimize(commands, logger=logger)
assert any(record.filename.endswith("path_planner_optimizer.py") for record in caplog.records)
```

## 3. Pruebas de Integración CLI y Flag --dev
- Se testea que el flag `--dev` activa el modo desarrollador y stacktrace extendido.
- Ejemplo:
```python
# tests/unit_tests/test_run_dev_flag.py
out, err, code = run_with_args(['--dev', '--input', 'no_existe.svg'])
assert '[DEV] Modo desarrollador activo' in err or '[DEV] Modo desarrollador activo' in out
assert 'Traceback' in err or 'Traceback' in out
```

## 4. Buenas Prácticas
- Usar `caplog` de pytest para asertar sobre logs.
- Inyectar siempre el logger en los tests, nunca usar el global.
- Verificar tanto el contenido como el formato de los logs.

---
Para más detalles, ver los archivos de test en `tests/unit_tests/` y la guía en `docs/logger_integration.md`.
