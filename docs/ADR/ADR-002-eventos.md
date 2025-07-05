# ADR-002: Gestión de Eventos y Desacoplamiento

## Estado
Aceptada

## Contexto
El sistema requiere un mecanismo para publicar y suscribirse a eventos (por ejemplo, generación de G-code, errores, auditoría) sin acoplar los componentes principales a acciones secundarias.

## Decisión
- El dominio define el puerto `EventBusPort` para eventos.
- La infraestructura implementa el gestor de eventos (`EventManager`).
- El contenedor inyecta el gestor de eventos como dependencia transversal.
- Los casos de uso y la CLI pueden publicar y suscribirse a eventos.

## Consecuencias
- Permite extensión futura (notificaciones, auditoría, plugins) sin modificar la lógica principal.
- Facilita pruebas y desacoplamiento.

## Fecha
2025-07-05
