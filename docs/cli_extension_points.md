# Puntos de extensión: CLI SvgToGcodeApp

Esta guía describe cómo agregar nuevas operaciones, modos o workflows a la CLI siguiendo la arquitectura actual.

## 1. Agregar una nueva operación (Operation)
- Crear una clase en `cli/operations/` que implemente la lógica de la operación.
- Instanciar la operación en el diccionario `self.operations` de `SvgToGcodeApp`.
- Asociar la operación a un número o clave para su selección.

## 2. Agregar un nuevo modo (ModeStrategy)
- Crear una clase en `cli/modes/` que implemente la interfaz de modo (ejemplo: `InteractiveModeStrategy`).
- Seleccionar el modo en `SvgToGcodeApp` según los argumentos (`self.mode_strategy = ...`).
- Asegurarse de que el modo invoque las operaciones/workflows adecuadas.

## 3. Agregar un nuevo workflow
- Crear la clase workflow en `application/workflows/`.
- Instanciar el workflow en `SvgToGcodeApp` y agregarlo al diccionario `workflows`.
- Asociar el workflow a una operación o modo según corresponda.

## 4. Extender la gestión de eventos
- Agregar nuevos eventos en `domain/events/events.py`.
- Suscribir handlers en `cli/utils/cli_event_manager.py`.
- Usar `event_manager.publish(event)` para emitir eventos desde workflows u operaciones.

## 5. Recomendaciones
- Mantener las dependencias inyectadas vía constructor o container.
- No modificar directamente la clase principal; usar factories y diccionarios para registrar extensiones.
- Documentar cada nueva operación, modo o workflow en este archivo.

---

> Esta estructura permite extender la CLI sin modificar el núcleo, cumpliendo OCP y facilitando la colaboración.
