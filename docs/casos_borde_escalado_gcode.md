# Casos Borde en el Escalado de GCODE

Este documento describe los casos borde identificados para el proceso de escalado de archivos GCODE, así como las recomendaciones y el manejo implementado en el sistema.

---

## 1. Dimensiones originales nulas (ancho o alto = 0)
- **Descripción:** El GCODE analizado no contiene movimientos que permitan calcular un ancho o alto mayor a cero.
- **Riesgo:** No se puede calcular un factor de escala válido (división por cero).
- **Manejo:** El sistema aborta el proceso y muestra un mensaje de error claro al usuario: "Dimensiones originales inválidas para escalado."

## 2. Dimensiones originales muy pequeñas (por ejemplo, < 1 mm)
- **Descripción:** El GCODE tiene un área muy pequeña, lo que puede llevar a factores de escala muy grandes.
- **Riesgo:** Coordenadas escaladas fuera de rango, pérdida de precisión, posibles problemas mecánicos.
- **Manejo:** Se recomienda advertir al usuario y establecer un límite mínimo de dimensiones aceptables. Actualmente, el sistema permite el escalado pero se sugiere monitorear este caso.

## 3. Área objetivo menor que el mínimo permitido por hardware
- **Descripción:** El área objetivo configurada es menor que el área mínima que puede manejar la máquina.
- **Riesgo:** El GCODE resultante puede no ser ejecutable o dañar el hardware.
- **Manejo:** Se recomienda validar el área objetivo antes de escalar y abortar el proceso si es demasiado pequeña.

## 4. GCODE que representa solo un punto o una línea
- **Descripción:** Todas las coordenadas son iguales (punto) o una dimensión es cero (línea).
- **Riesgo:** El área es nula o degenerada, el escalado no tiene sentido práctico.
- **Manejo:** El sistema aborta el proceso y notifica al usuario que el contenido no es escalable.

## 5. Comandos no estándar o comentarios que afectan el análisis de dimensiones
- **Descripción:** El GCODE contiene líneas no reconocidas o comentarios que dificultan el análisis.
- **Riesgo:** Las dimensiones calculadas pueden ser incorrectas.
- **Manejo:** El analizador ignora comentarios y líneas no reconocidas. Si no se pueden calcular dimensiones válidas, se aborta el proceso.

---

**Recomendación:**
- Mantener y actualizar esta documentación a medida que se detecten nuevos casos borde en producción o durante el desarrollo.
- Implementar advertencias y validaciones adicionales según la experiencia de usuario y feedback del equipo.
