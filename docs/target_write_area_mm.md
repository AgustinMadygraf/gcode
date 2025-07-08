# Documentación de `TARGET_WRITE_AREA_MM`

## ¿Qué es?
`TARGET_WRITE_AREA_MM` es un parámetro de configuración que define el área objetivo (ancho x alto, en milímetros) donde debe inscribirse el contenido generado (por ejemplo, GCODE) en la superficie de la máquina (plotter/CNC).

## Ubicación
Se encuentra en el archivo de configuración principal: `infrastructure/config/config.json`.

## Formato
- Tipo: lista de dos números flotantes `[ancho_mm, alto_mm]`
- Ejemplo: `[210.0, 148.0]` (A5 horizontal)

## Uso
- El sistema utiliza este valor para calcular el factor de escala máximo que permite que el contenido se ajuste completamente dentro del área objetivo, manteniendo la relación de aspecto.
- Si el contenido original es más grande, se reduce proporcionalmente.
- Si es más pequeño, puede escalarse para aprovechar el área disponible.
- El área objetivo nunca debe exceder el área máxima física de la máquina (`PLOTTER_MAX_AREA_MM`).

## Validaciones
- Si el valor es inválido (no es una lista de dos números positivos), se usa el valor por defecto definido en `config_default.json`.
- El sistema valida que el contenido escalado nunca exceda el área objetivo.

## Recomendaciones
- Ajusta este valor según el tamaño del papel o superficie que vayas a utilizar.
- Para formatos estándar, puedes usar:  
  - A4 horizontal: `[297.0, 210.0]`  
  - A4 vertical: `[210.0, 297.0]`  
  - A5 horizontal: `[210.0, 148.0]`
- Si tienes dudas sobre el área máxima soportada, consulta el parámetro `PLOTTER_MAX_AREA_MM`.

---

**Última actualización:** Julio 2025
