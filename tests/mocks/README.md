# Mocks para pruebas unitarias

Este directorio contiene implementaciones simuladas (mocks) de interfaces y componentes
para facilitar pruebas unitarias aisladas según los principios de Clean Architecture.

## Estructura

- `mock_gcode_generator.py` - Mocks para generación de GCode
- `mock_path_sampler.py` - Mocks para muestreo de rutas
- `mock_strategy.py` - Mocks para estrategias de transformación
- `mock_svg_loader.py` - Mocks para carga de archivos SVG
- `mock_use_case.py` - Mocks para casos de uso

## Mejores prácticas

1. **Aislar los tests**: Usar estos mocks para evitar dependencias de capas externas
2. **Mantener consistencia**: Usar una única implementación de mock por interfaz
3. **Evitar lógica compleja**: Los mocks deben ser simples, deterministicos y predecibles
4. **Separar mocks por responsabilidad**: Un archivo por tipo de componente/puerto simulado

## Convención de nombres

- Prefijo `Mock` para implementaciones de puertos/interfaces de dominio
- Prefijo `Dummy` para componentes más simples usados en casos de uso

## Cómo usar

```python
from tests.mocks.mock_svg_loader import MockSvgLoader
from tests.mocks.mock_gcode_generator import MockGCodeGenerator

# Configura tus tests con los mocks
svg_loader = MockSvgLoader(svg_file_path)
gcode_gen = MockGCodeGenerator()

# Usa los mocks para probar tu componente real aisladamente
my_component = MyComponent(svg_loader, gcode_gen)
result = my_component.process()
```
