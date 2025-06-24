# Arquitectura del Proyecto GCode

## Introducción
Este documento describe la arquitectura del proyecto GCode, basada en los principios de Clean Architecture. El objetivo es mantener una separación clara de responsabilidades, facilitar la escalabilidad y asegurar la mantenibilidad del código.

## Mapa de Capas
```
gcode/
├── adapters/                  # Adaptadores de entrada/salida (implementaciones de puertos)
├── application/
│   └── use_cases/            # Casos de uso y orquestación
│       └── path_processing/  # Orquestación de conversión de paths a G-code
├── cli/                      # Interfaz de usuario (CLI)
├── infrastructure/
│   └── config/               # Configuración (migrada desde config/)
├── domain/                   # Entidades, modelos, lógica de negocio, puertos
│   └── ports/                # Puertos (interfaces) de dominio
│   └── services/
│       └── optimization/     # Optimizadores de G-code (lógica de negocio)
├── data/svg_input/           # Archivos SVG de entrada
├── data/gcode_output/        # Archivos G-code generados
├── tests/                    # Tests unitarios y de integración
└── docs/                     # Documentación
```

## Cambios recientes (06/2025)
- Adaptadores consolidados en `adapters/`.
- Optimizadores movidos a `domain/services/optimization/`.
- Inyección de configuración en adaptadores (usando `infrastructure.config.Config`).
- Eliminados tests y código legacy.
- Orquestación de conversión de paths a G-code migrada a `application/use_cases/path_processing/path_conversion_service.py`.
- Puerto de conversión definido en `domain/ports/path_conversion_port.py`.
- Archivo `domain/path_conversion_service.py` deprecado y marcado para eliminación.
- Estructura y nomenclatura alineadas a Clean Architecture.

## Descripción de Capas

### 1. Dominio (`domain/`)
- Contiene entidades, modelos, lógica de negocio y puertos (interfaces).
- No depende de ninguna otra capa.

### 2. Aplicación (`application/`)
- Orquesta casos de uso y coordina servicios de dominio.
- Depende solo de la capa de dominio.
- La orquestación de conversión de paths a G-code reside aquí.

### 3. Infraestructura (`infrastructure/`, `infrastructure/config/`)
- Implementa adaptadores, servicios externos y detalles técnicos.
- Depende de dominio y aplicación, nunca al revés.

### 4. Interfaz (`cli/`)
- Provee la interfaz de usuario (CLI).
- Puede interactuar con aplicación e infraestructura.

## Reglas de Dependencia
- Las dependencias siempre apuntan hacia el dominio.
- La infraestructura y la interfaz nunca deben ser importadas por dominio o aplicación.
- Los puertos (interfaces) se definen en dominio y se implementan en infraestructura/adapters.

## Patrón de Dependencias Correcto

- Los puertos (interfaces) del dominio (`domain/ports/`) nunca importan adaptadores, infraestructura ni aplicación.
- Los adaptadores (`adapters/`) implementan los puertos y dependen de ellos, nunca al revés.
- No existen ciclos de importación entre capas.
- Si se detecta una dependencia cruzada, aplicar inversión de dependencias (crear interfaz en dominio y mover implementación a adaptadores/infrastructure).

Este patrón asegura la independencia y testabilidad del dominio, y previene acoplamientos indebidos.

## Principios Clave
- **Inversión de dependencias:** El dominio define interfaces, la infraestructura/adapters las implementa.
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
