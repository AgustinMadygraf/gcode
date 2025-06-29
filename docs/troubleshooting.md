# Troubleshooting (Solución de problemas)

## Problemas comunes

### El comando `python run.py` no hace nada o muestra error de importación
- Asegúrate de estar en la raíz del proyecto y de tener Python 3.8+ instalado.
- Verifica que ejecutas `python run.py` y **no** `cli/main.py` directamente.

### Mensaje: `[ERROR] Archivo no encontrado`
- Revisa la ruta y nombre del archivo pasado con `--input`.
- Si usas modo interactivo, asegúrate de seleccionar un archivo válido.

### Mensaje: `Permission denied` o problemas de escritura
- Verifica permisos de escritura en la carpeta de salida (`data/gcode_output/` o la que configures).
- En Windows, ejecuta la terminal como administrador si es necesario.

### Los colores no se ven bien en mi terminal
- Usa el flag `--no-color` para desactivar colores ANSI.
- En Windows, algunos terminales antiguos no soportan colores.

### Los mensajes aparecen en español pero quiero inglés
- Usa el flag `--lang en` para mostrar los mensajes en inglés.

### No se genera el archivo de salida esperado
- Si no especificas `--output`, el sistema genera un nombre automáticamente en la carpeta de salida.
- Revisa los logs o mensajes de error para más detalles.

### ¿Cómo reporto un bug?
- Abre un issue en el repositorio o contacta al mantenedor con el mensaje de error y los pasos para reproducirlo.
