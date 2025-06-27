# Plan de Optimización SVG → GCODE

## Resumen Ejecutivo

Este documento detalla el plan de implementación para optimizar el proceso de conversión de SVG a GCODE usando un enfoque en tres etapas: optimización de entrada (SVG), optimización de transformación, y optimización de salida (GCODE).

## 1. Análisis de la Estructura Actual

La arquitectura actual sigue los principios de Clean Architecture con las siguientes capas:

- **Dominio** (`domain/`): Entidades, modelos, servicios y puertos
- **Aplicación** (`application/`): Casos de uso, workflows, orquestación
- **Adaptadores** (`adapters/`): Implementaciones de puertos
- **Infraestructura** (`infrastructure/`): Configuración, servicios técnicos
- **CLI** (`cli/`): Interfaz de línea de comandos

## 2. Enfoque de Optimización en Tres Etapas

### 2.1. Etapa SVG (Entrada)
- Muestreo adaptativo basado en curvatura
- Reconocimiento de primitivas geométricas
- Optimización de paths

### 2.2. Etapa de Transformación (Intermedia)
- Conversión directa de primitivas a GCODE óptimo
- Generación de comandos de arco (G2/G3)
- Ajuste dinámico de velocidad

### 2.3. Etapa GCODE (Salida)
- Optimización de trayectorias
- Compresión inteligente de comandos
- Minimización de movimientos no productivos

## 3. Plan de Implementación

### Fase 1: Optimización de Entrada (SVG)

#### 1.1. Implementar AdaptivePathSampler
- Crear clase que extiende el PathSampler actual
- Algoritmo de densidad variable según curvatura
- Integración con PathProcessingService

#### 1.2. Desarrollar SVGPrimitiveDetector
- Reconocimiento de círculos, elipses, rectángulos
- Análisis de paths para identificar formas primitivas
- Conversión de primitivas a representación interna optimizada

#### 1.3. Actualizar GeometryService
- Añadir cálculo de curvatura
- Implementar simplificación de paths avanzada
- Crear funciones de reconocimiento de formas

### Fase 2: Optimización de Transformación

#### 2.1. Mejorar GCodeGenerationService
- Implementar generación de comandos G2/G3 para arcos
- Añadir ajuste de velocidad basado en geometría
- Mejorar manejo de primitivas detectadas

#### 2.2. Crear PrimitiveToGCodeConverter
- Conversión directa de círculos a G2/G3
- Manejo optimizado de elipses y rectángulos
- Integración con pipeline de generación

#### 2.3. Implementar VelocityOptimizer
- Ajuste dinámico de velocidad (comando F)
- Adaptación según curvatura y longitud de segmento
- Configuración de límites por perfil de máquina

### Fase 3: Optimización de Salida (GCODE)

#### 3.1. Mejorar Optimizadores Existentes
- Extender ArcOptimizer para manejar más casos
- Actualizar LineOptimizer para casos complejos
- Implementar optimización basada en propiedades físicas

#### 3.2. Crear TrajectoryOptimizer
- Planificación global de rutas
- Optimización de orden de trazos
- Minimización de movimientos no productivos

#### 3.3. Implementar SmartGCodeCompressor
- Alternancia inteligente entre modos absoluto/relativo
- Eliminación avanzada de redundancias
- Compresión del tamaño de archivo final

### Fase 4: Configuración e Integración

#### 4.1. Extender Sistema de Configuración
- Añadir parámetros para todas las optimizaciones
- Crear perfiles predefinidos (calidad, velocidad, tamaño)
- Documentar opciones de configuración

#### 4.2. Actualizar CLI y Flujos de Trabajo
- Añadir banderas para activar optimizaciones
- Mostrar estadísticas de optimización
- Mantener compatibilidad con flujos existentes

#### 4.3. Implementar Sistema de Métricas
- Medir tiempos de procesamiento
- Calcular tasas de compresión
- Evaluar precisión geométrica

## 4. Cronograma

1. **Fase 1 (Optimización SVG)**: 1 semana
2. **Fase 2 (Optimización Transformación)**: 1 semana
3. **Fase 3 (Optimización GCODE)**: 1 semana
4. **Fase 4 (Configuración e Integración)**: 1 semana
5. **Pruebas y Documentación**: 1 semana

## 5. Criterios de Éxito

1. Reducción del tamaño de archivos GCODE (>20%)
2. Mejora en la precisión de reproducción de curvas
3. Reducción de tiempo de ejecución en máquina CNC/plotter
4. Mantener compatibilidad con flujos de trabajo existentes
