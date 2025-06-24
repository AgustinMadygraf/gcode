# Plan de migración de mocks en tests

Este documento contiene las instrucciones para continuar la migración de mocks a la nueva estructura
centralizada en `/tests/mocks/`.

## Archivos pendientes de migración

Los siguientes archivos contienen clases mock que deben ser migradas:

### Tests unitarios
- `tests/unit_tests/test_path_sampler.py` - Contiene `MockSegment`
- `tests/unit_tests/test_geometry_service.py` - Contiene `MockSegment` 
- `tests/unit_tests/test_filename_service.py` - Contiene `DummyConfigProvider`
- `tests/unit_tests/test_domain_factory.py` - Contiene `DummyConfig`
- `tests/unit_tests/test_deduplication.py` - Contiene `DummySegment`

### Tests de integración
- `tests/integration_tests/test_gcode_generator_integration.py` - Contiene múltiples mocks
- `tests/integration_tests/test_gcode_cmdup.py` - Contiene múltiples mocks
- `tests/integration_tests/print_gcode_svg_minimo.py` - Contiene `MockStrategy`
- `tests/integration_tests/print_gcode_strokes.py` - Contiene múltiples mocks

## Instrucciones de migración

1. Para cada archivo pendiente:
   - Identificar los mocks y sus dependencias
   - Crear archivo(s) adecuado(s) en `/tests/mocks/` si no existen ya
   - Mover la implementación del mock al nuevo archivo
   - Actualizar el archivo de test para importar desde `/tests/mocks/`
   
2. Recomendaciones para el proceso:
   - Migrar primero los mocks que son más utilizados (reutilización)
   - Agrupar mocks similares en el mismo archivo (ej: mock_geometry.py para Point, Segment, etc.)
   - Mantener la compatibilidad con tests existentes durante la migración
   - Ejecutar tests después de cada migración para verificar funcionamiento

3. Tests de integración:
   - Evaluar si es apropiado usar mocks en tests de integración
   - Para mocks necesarios en integración, crear archivos separados en `/tests/mocks/integration/`

## Beneficios esperados

- Eliminar duplicación de código
- Mejorar mantenibilidad de tests
- Garantizar consistencia en comportamiento simulado
- Facilitar la detección de violaciones a Clean Architecture en tests
