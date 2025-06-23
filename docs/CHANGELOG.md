# CHANGELOG.md

## [Unreleased]
### Corregido
- Se corrigió el problema de trazos duplicados al convertir SVG a G-code:
  - `SvgLoader.get_subpaths()` ahora preserva la continuidad de los paths y solo divide cuando hay una discontinuidad real.
  - `GCodeGenerator.generate_gcode_commands()` elimina puntos consecutivos idénticos (con tolerancia), evitando comandos G1 redundantes.
- Se agregaron pruebas automatizadas para verificar la ausencia de duplicados y la correcta preservación de la continuidad.
