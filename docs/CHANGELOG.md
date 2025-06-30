## [2025-06-30] Optimización avanzada del feed rate en G-code

- El sistema ahora incluye el feed rate (`F...`) solo en el primer `G1` de cada trazo y cada vez que el valor cambia, o tras un `G0`/cambio de herramienta.
- Esto maximiza compatibilidad y robustez en controladores CNC/plotter.
- Tests de integración y unitarios actualizados para validar el nuevo comportamiento.
- Documentación y ejemplos actualizados en el README.
