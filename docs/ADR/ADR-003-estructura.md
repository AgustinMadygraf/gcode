# ADR-003: Estructura de Carpetas y Separación de Capas

## Estado
Aceptada

## Contexto
El crecimiento del proyecto y la adopción de Clean Architecture requieren una estructura de carpetas que refleje claramente las capas y responsabilidades.

## Decisión
- Se adopta la estructura: `adapters/`, `application/`, `domain/`, `infrastructure/`, `cli/`, `tests/`, `docs/`, `data/`.
- Cada carpeta representa una capa o contexto bien definido.
- No se permite mezclar responsabilidades entre capas.
- Las dependencias siempre fluyen hacia el dominio.

## Consecuencias
- Facilita la mantenibilidad y escalabilidad.
- Reduce el riesgo de ciclos y acoplamientos indebidos.
- Permite identificar rápidamente la ubicación de cada responsabilidad.

## Fecha
2025-07-05
