# markdown_to_gcode_workflow.py
import os
from HersheyFonts import HersheyFonts  # ✅

class MarkdownToGcodeWorkflow:
    " Workflow para convertir Markdown a GCODE. "
    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config

    def run(self, input_path, output_path=None):
        " Ejecuta el workflow de conversión de Markdown a GCODE. "
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except (IOError, OSError) as e:
            self.presenter.print(f"Error al leer Markdown: {e}", color='red')
            return False

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.join('data', 'gcode_output')
        os.makedirs(output_dir, exist_ok=True)
        if output_path is None:
            output_file = os.path.join(output_dir, f"{base_name}.gcode")
        else:
            output_file = output_path

        # --- Leer área de escritura y margen ---
        area = self.config.TARGET_WRITE_AREA_MM if hasattr(self.config, 'TARGET_WRITE_AREA_MM') else [297.0, 210.0]
        ancho_area, alto_area = area
        margen = 5.0
        ancho_util = ancho_area - 2 * margen
        alto_util = alto_area - 2 * margen

        # --- Configurar la fuente y calcular escala ---
        font = HersheyFonts()
        font.load_default_font('futural')
        font.normalize_rendering(10)  # altura base de letra

        lineas = [line for line in markdown_content.splitlines() if line.strip()]
        n_lineas = len(lineas)
        # Calcular y_step y scale para que todo el texto entre en el área útil
        y_step = (alto_util / max(n_lineas, 1)) * 0.6  # Factor para reducir salto de línea
        # Calcular ancho máximo de línea
        max_len = max([len(line) for line in lineas], default=1)
        # Ancho de una letra en la fuente
        ancho_letra = font.width if hasattr(font, 'width') else 10.0
        scale_x = ancho_util / (max_len * ancho_letra)
        scale_y = y_step / 10.0  # 10 es la altura base de la fuente
        scale = min(scale_x, scale_y)

        x_start = margen
        y_start = margen
        y = y_start

        gcode_lines = [f"; GCODE generado desde Markdown: {input_path}"]
        for line in lineas:
            gcode_lines.append(f"; Escribiendo: {line}")
            for (x1, y1), (x2, y2) in font.lines_for_text(line):
                gcode_lines.append(
                    f"G0 X{(x_start + x1*scale):.2f} Y{(y + y1*scale):.2f}"
                )
                gcode_lines.append("M3")
                gcode_lines.append(
                    f"G1 X{(x_start + x2*scale):.2f} Y{(y + y2*scale):.2f} F1000"
                )
                gcode_lines.append("M5")
            y += y_step
        gcode_lines.append("; --- Fin del contenido ---")
        # Guardar el archivo GCODE
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(gcode_lines))
            self.presenter.print(f"Archivo GCODE generado: {output_file}", color='green')
            return True
        except (IOError, OSError) as e:
            self.presenter.print(f"Error al guardar GCODE: {e}", color='red')
            return False
