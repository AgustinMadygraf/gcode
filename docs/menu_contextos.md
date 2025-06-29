# Diseño de menú principal adaptable al contexto

## 1. Contextos identificados
- Modo interactivo (sin argumentos de entrada/salida)
- Modo batch/no-interactive (`--no-interactive`)
- Archivo de entrada especificado (`--input`)
- No hay archivos SVG/GCODE disponibles
- Plugins/extensiones detectados

## 2. Reglas sugeridas
- Si `--no-interactive`: no mostrar menú, solo ejecutar acción y salir.
- Si `--input` y `--output` presentes: saltar selección de archivos, mostrar solo confirmación/avance.
- Si no hay archivos SVG/GCODE: mostrar solo opciones "cambiar carpeta" o "salir".
- Si hay plugins: agregar opciones dinámicas al menú.
- Por defecto: mostrar menú clásico (SVG→GCODE, Optimizar, Salir).

## 3. Ejemplos de flujo
- **Batch:** `python run.py --no-interactive -i a.svg -o b.gcode` → Sin menú.
- **Sin archivos:** Menú solo muestra "salir" o "cambiar carpeta".
- **Con plugins:** Menú muestra nuevas opciones.

## 4. Consideraciones
- Siempre mostrar opción "salir".
- Documentar cambios en README y ayuda CLI.
- Agregar tests para cada contexto.

---

# Plan de tests sugeridos
- Menú clásico se muestra si no hay argumentos.
- Menú se omite en modo batch.
- Menú se adapta si no hay archivos.
- Menú incluye plugins si existen.
