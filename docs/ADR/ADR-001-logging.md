# ADR-001: Política de Logging y Eliminación de Logger Global

## Estado
Aceptada

## Contexto
El proyecto GCode requiere trazabilidad y control de logs en todos los flujos de ejecución, incluyendo CLI, futuros entrypoints (API, plugins) y escenarios concurrentes. Históricamente existía una instancia global de logger, lo que generaba riesgos de efectos colaterales y acoplamientos ocultos.

## Decisión
- Se elimina toda instancia global de logger.
- El logger debe ser inyectado explícitamente en todos los componentes que lo requieran.
- Se usará siempre `InfraFactory.get_logger()` para obtener loggers configurados por contexto.
- Cualquier intento de acceder a un logger global será considerado un error de arquitectura.

## Consecuencias
- Mayor seguridad y trazabilidad en escenarios concurrentes.
- Facilita el testeo y la extensión a nuevos entrypoints.
- Requiere disciplina en la inyección de dependencias.

## Fecha
2025-07-05
