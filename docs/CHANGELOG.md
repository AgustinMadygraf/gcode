# CHANGELOG.md

## [Unreleased]
### Corregido
- Se corrigió el problema de trazos duplicados al convertir SVG a G-code:
  - `SvgLoader.get_subpaths()` ahora preserva la continuidad de los paths y solo divide cuando hay una discontinuidad real.
  - `GCodeGenerator.generate_gcode_commands()` elimina puntos consecutivos idénticos (con tolerancia), evitando comandos G1 redundantes.
- Se agregaron pruebas automatizadas para verificar la ausencia de duplicados y la correcta preservación de la continuidad.

### Refactorización (06/2025)
- Lógica de bounding box migrada de la CLI a `domain/services/geometry.py`.
- Lógica de generación de nombres migrada de la CLI a `application/generation/filename_service.py`.
- Se crearon tests unitarios para ambos servicios.
- Eliminada la interfaz `ISvgLoader` (usar `SvgLoaderPort`).
- Se creó `domain/path_conversion_service.py` como interfaz de orquestación de conversión de paths a G-code.
