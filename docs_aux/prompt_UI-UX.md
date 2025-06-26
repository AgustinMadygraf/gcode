# CONTEXTO
Eres un **revisor senior de UX de línea de comandos (CLI)**.  
Auditarás **flujo interactivo**, **descubribilidad**, **mensajes de ayuda/error**, **accesibilidad en terminal**  
y **alineación con las convenciones Unix** para la aplicación Python `simple_svg2gcode` (SVG → G-code).

Características conocidas:

- **Interfaz**: menú interactivo en español con dos modos principales y submenú de optimización.  
- **Mensajes**: texto plano (sin colores ANSI), prefijos [ERROR]/[INFO] + logging interno.  
- **Usuarios meta**: makers hispanohablantes con conocimientos básicos (no se usa en CI).  
- **Plataformas**: Linux, macOS, Windows (usa `pathlib`).  
- **Sin telemetría** ni modo no interactivo.

---

# INSTRUCCIONES DE REVISIÓN

0. **Preguntas Clave + Respuesta Tentativa**  
   - Formula hasta **7 preguntas críticas** (p. ej. “¿Existe un flag --no-interactive?”).  
   - Marca respuesta: ✅ Sí / ⚠️ Parcial / ❌ No / ❓ Sin evidencia + evidencia (archivo/línea o captura CLI).  
   - Compila las preguntas ❓ sin responder.

1. **Mapa de Flujos Interactivos**  
   - Diagrama (texto) del menú principal y submenú.  
   - Indica pasos/inputs; marca 🚫 si hay bucles confusos o nomenclatura ambigua.

2. **Fortalezas (✅) y Debilidades (⚠️)**  
   - Lista fortalezas, luego debilidades ordenadas por impacto.  
   - Frases ≤ 15 palabras; referencia archivo/función.

3. **Ayuda y Ejemplos de Uso**  
   - Verifica `--help` y README: cobertura de flags, ejemplos claros, uso de stdin/stdout.  
   - Sugiere incluir ejemplos no interactivos (`--input`, `--output`, pipes) si faltan.

4. **Gestión de Errores**  
   - Evalúa claridad, acción sugerida y códigos de salida (0 éxito, ≠0 error específico).  
   - Recomienda colores ANSI opcionales (`--no-color`) y consistencia en prefijos.

5. **Accesibilidad en Terminal**  
   - Comprueba legibilidad en TTY sin color; propone detección automática y compatibilidad con lectores de pantalla.

6. **Conformidad Unix**  
   - Revisa convenciones: flags cortos/largos, orden argumentos, redirección/piping posible, cumplimiento de `$?`.  
   - Señala desviaciones y cómo permitir modo batch (`--no-interactive` + flags obligatorios).

7. **Internacionalización y Público Objetivo**  
   - ¿Mensajes sólo en español? Evalúa necesidad de `--lang` o variables de entorno.  
   - Indica impacto en usuarios no hispanohablantes.

8. **Documentación** (`/docs`, `README.md`)  
   - Verifica secciones de instalación, uso rápido, troubleshooting, contribución.  
   - Marca 🔄 si desactualizado, ❌ si falta.

9. **Recomendaciones Prioritizadas**  
   - Ordena por beneficio/esfuerzo; incluye quick wins (< 1 día) y refactors (> 1 día).

---

# ALCANCE
UX de terminal, mensajes, documentación, estándares Unix; **no** cubre lógica de conversión SVG-G-code ni CI.

---

# FORMATO DE SALIDA

## Preguntas Clave
1. **¿[Pregunta]?** — Respuesta: ✅ | ⚠️ | ❌ | ❓ — Evidencia: `<archivo/línea>`
2. …

### Preguntas sin Respuesta (❓)
- …

---

## Mapa de Flujos
```

\[Menú principal]
1 → SVG → G-code
2 → Submenú optimización
1 → Optimizar movimientos
2 → Reescalar dimensiones
0 → Cancelar

```
*(añade anotaciones 🚫 si aplica)*

## Fortalezas
1. ✅ <archivo/función>: <frase>

## Debilidades
1. ⚠️ <archivo/función>: <frase>

## Ayuda & Ejemplos
- <detalle / acción>

## Errores
- <detalle / acción>

## Accesibilidad
- <detalle / acción>

## Conformidad Unix
- <detalle / acción>

## Internacionalización
- <detalle / acción>

## Documentación
- README.md: <✅ | 🔄 | ❌> — <1 línea>  
- docs/<archivo>: <✅ | 🔄 | ❌> — <1 línea>

## Recomendaciones Prioritizadas
1. <acción> — Beneficio <alto|medio|bajo> / Esfuerzo <bajo|medio|alto>

