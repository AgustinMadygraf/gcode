# Arquitectura del Proyecto GCode

## Introducción
Este documento describe la arquitectura del proyecto GCode, basada en los principios de Clean Architecture. El objetivo es mantener una separación clara de responsabilidades, facilitar la escalabilidad y asegurar la mantenibilidad del código.

## Mapa de Capas
```
gcode/
├── application/         # Capa de Aplicación (Casos de uso)
│   ├── generation/      # Ejemplo: generación de nombres de archivo (FilenameService)
│   └── ...              # Otros casos de uso
├── cli/                # Capa de Interfaz (UI/CLI)
├── config/             # Infraestructura (Configuración)
├── domain/             # Capa de Dominio (Modelos, lógica de negocio, puertos)
│   ├── services/        # Ejemplo: GeometryService para bounding box
│   └── path_conversion_service.py # Orquestador de conversión de paths a G-code
├── infrastructure/     # Infraestructura (implementaciones, adaptadores)
│   └── svg_loader.py   # Loader de SVG (implementa SvgLoaderPort)
├── docs/               # Documentación
```

## Cambios recientes (06/2025)
- La lógica de cálculo de bounding box fue trasladada de la CLI a `domain/services/geometry.py`.
- La generación de nombres de archivos G-code fue trasladada de la CLI a `application/generation/filename_service.py`.
- Se crearon tests unitarios dedicados para ambos servicios.
- Se eliminó la interfaz redundante `ISvgLoader` y se consolidó el uso de `SvgLoaderPort` como interfaz oficial.
- Se creó `domain/path_conversion_service.py` como interfaz de orquestación de conversión de paths a G-code.

## Descripción de Capas

### 1. Dominio (`domain/`)
- Contiene entidades, modelos, lógica de negocio y puertos (interfaces).
- No depende de ninguna otra capa.

### 2. Aplicación (`application/`)
- Orquesta casos de uso y coordina servicios de dominio.
- Depende solo de la capa de dominio.

### 3. Infraestructura (`infrastructure/`, `config/`)
- Implementa adaptadores, servicios externos y detalles técnicos.
- Depende de dominio y aplicación, nunca al revés.

### 4. Interfaz (`cli/`)
- Provee la interfaz de usuario (CLI).
- Puede interactuar con aplicación e infraestructura.

## Reglas de Dependencia
- Las dependencias siempre apuntan hacia el dominio.
- La infraestructura y la interfaz nunca deben ser importadas por dominio o aplicación.
- Los puertos (interfaces) se definen en dominio y se implementan en infraestructura.

## Principios Clave
- **Inversión de dependencias:** El dominio define interfaces, la infraestructura las implementa.
- **Separación de responsabilidades:** Cada capa tiene un propósito claro.
- **DRY:** Evitar duplicidad de lógica entre capas.

## Diagrama Simplificado

```
[ CLI ]
   |
[ Application ]
   |
[ Domain ] <--- [ Infrastructure ]
```

## Notas y Recomendaciones
- Mantener la documentación de modelos e invariantes en `docs/domain_models.md`.
- Documentar cambios relevantes en `docs/CHANGELOG.md`.
- Revisar periódicamente dependencias para evitar inversiones indebidas.

---

_Última actualización: 23/06/2025_
