# Ejecución avanzada y ejemplos

## Uso no interactivo (batch/script)

Puedes automatizar la conversión y optimización usando argumentos:

- `--input` (`-i`): Archivo de entrada (SVG o GCODE)
- `--output` (`-o`): Archivo de salida (opcional)
- `--optimize`: Optimiza movimientos G1→G0 en GCODE
- `--rescale <factor>`: Reescala GCODE por el factor indicado (ej: 1.5)
- `--lang <es|en>`: Idioma de los mensajes
- `--no-color`: Desactiva colores en la terminal
- `--no-interactive`: Ejecuta sin menús ni prompts
- `--dev`, `--debug`: Activa modo desarrollador (logging DEBUG, stacktrace extendido)
- `--save-config`: Guarda los argumentos actuales como preferencias de usuario persistentes.
- `--config <ruta>`: Usa un archivo de configuración personalizado (JSON).

### Ejemplos

**Convertir SVG a GCODE (no interactivo):**
```powershell
python run.py --no-interactive --input dibujo.svg --output resultado.gcode
```

**Optimizar movimientos en un GCODE existente:**
```powershell
python run.py --no-interactive --input archivo.gcode --optimize
```

**Reescalar un GCODE existente:**
```powershell
python run.py --no-interactive --input archivo.gcode --rescale 1.5
```

**Mostrar ayuda y opciones:**
```powershell
python run.py --help
```

### Ejemplos con redirección y pipes

**Convertir SVG desde stdin y escribir G-code a stdout:**
```bash
cat dibujo.svg | python run.py --no-interactive --input - --output - > resultado.gcode
```

**Optimizar un G-code usando redirección:**
```bash
python run.py --no-interactive --input archivo.gcode --optimize --output - > optimizado.gcode
```

**Usar en un pipeline (SVG → G-code → optimización):**
```bash
cat dibujo.svg | python run.py --no-interactive --input - --output - | \
  python run.py --no-interactive --input - --optimize --output resultado.gcode
```

> **Nota:** En entornos sin TTY (pipes/redirección), la barra de progreso imprime líneas de avance tipo "Progreso: XX%" para mayor accesibilidad y seguimiento en logs.
