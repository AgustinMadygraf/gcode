"""
Caso de uso para reescalar archivos GCODE manteniendo su relación de aspecto.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import re
import math
from domain.services.validation.gcode_validator import GCodeValidator

class GcodeRescaleUseCase:
    " Caso de uso para reescalar archivos GCODE manteniendo su relación de aspecto. "
    def __init__(self, filename_service, logger=None, config_provider=None):
        self.filename_service = filename_service
        self.logger = logger
        self.config = config_provider

    def execute(self, gcode_file: Path, target_height: Optional[float] = None, target_width: Optional[float] = None) -> Dict[str, Any]:
        """
        Reescala un archivo GCODE para que encaje dentro de un área objetivo (ancho x alto), manteniendo la relación de aspecto.
        Si no se especifica target_width/target_height, se toma de la configuración.
        """
        if self.logger:
            self.logger.info(f"Reescalando archivo GCODE: {gcode_file}")
        with open(gcode_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Validar integridad G-code antes de procesar
        valido, error = GCodeValidator.validate([l.strip() for l in lines])
        if not valido:
            if self.logger:
                self.logger.error(f"Validación G-code fallida: {error}")
            raise ValueError(f"Archivo G-code inválido: {error}")
        dimensions = self._analyze_dimensions(lines)
        current_width = dimensions['width']
        current_height = dimensions['height']
        # Obtener área objetivo
        if self.config and hasattr(self.config, 'target_write_area_mm'):
            area_obj = self.config.target_write_area_mm
            area_target_width = area_obj[0]
            area_target_height = area_obj[1]
        else:
            area_target_width = 210.0
            area_target_height = 148.0
        max_width = target_width or area_target_width
        max_height = target_height or area_target_height
        # Validar que el área objetivo sea válida
        if max_width <= 0 or max_height <= 0:
            raise ValueError(f"Área objetivo inválida: ({max_width} x {max_height} mm). Debe ser mayor que cero.")
        # Validar que el área objetivo no exceda el área máxima de la plotter
        if self.config and hasattr(self.config, 'plotter_max_area_mm'):
            plotter_max_width, plotter_max_height = self.config.plotter_max_area_mm
            if max_width > plotter_max_width + 1e-3 or max_height > plotter_max_height + 1e-3:
                raise ValueError(f"El área objetivo ({max_width:.2f}x{max_height:.2f} mm) excede el área máxima de la plotter ({plotter_max_width:.2f}x{plotter_max_height:.2f} mm).")
        # Calcular factor de escala proporcional
        if current_width <= 0 or current_height <= 0:
            raise ValueError("Dimensiones originales inválidas para escalado.")
        scale_w = max_width / current_width
        scale_h = max_height / current_height
        scale_factor = min(scale_w, scale_h)
        scaled_lines, rescale_stats = self._rescale_gcode(lines, scale_factor)
        # Validar que el contenido escalado no exceda el área objetivo
        new_width = current_width * scale_factor
        new_height = current_height * scale_factor
        if new_width > max_width + 1e-3 or new_height > max_height + 1e-3:
            raise ValueError(f"El contenido escalado ({new_width:.2f}x{new_height:.2f} mm) excede el área objetivo ({max_width:.2f}x{max_height:.2f} mm).")
        # Generar nombre de archivo de salida manualmente
        output_dir = self.config.get_gcode_output_dir() if self.config else gcode_file.parent
        stem = gcode_file.stem
        scale_tag = f"_scaled_{int(new_width)}x{int(new_height)}"
        candidate = output_dir / f"{stem}{scale_tag}.gcode"
        # Evitar sobrescribir archivos existentes
        idx = 0
        final_candidate = candidate
        while final_candidate.exists():
            final_candidate = output_dir / f"{stem}{scale_tag}_v{idx:02d}.gcode"
            idx += 1
        output_file = final_candidate
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(scaled_lines))
        return {
            'output_file': output_file,
            'original_dimensions': dimensions,
            'new_dimensions': {
                'width': new_width,
                'height': new_height,
                'x_min': dimensions['x_min'] * scale_factor,
                'x_max': dimensions['x_max'] * scale_factor,
                'y_min': dimensions['y_min'] * scale_factor,
                'y_max': dimensions['y_max'] * scale_factor
            },
            'scale_factor': scale_factor,
            'commands_rescaled': rescale_stats
        }

    def _analyze_dimensions(self, gcode_lines: List[str]) -> Dict[str, float]:
        x_min, y_min = float('inf'), float('inf')
        x_max, y_max = float('-inf'), float('-inf')
        g0g1_pattern = re.compile(r'[gG][01]\s+.*?[xX]([\-\d.]+).*?[yY]([\-\d.]+)', re.IGNORECASE)
        g2g3_pattern = re.compile(r'[gG][23]\s+.*?[xX]([\-\d.]+).*?[yY]([\-\d.]+).*?[iI]([\-\d.]+).*?[jJ]([\-\d.]+)', re.IGNORECASE)
        current_x, current_y = 0.0, 0.0
        for line in gcode_lines:
            clean_line = line.split(';')[0].strip()
            match = g0g1_pattern.match(clean_line)
            if match:
                current_x, current_y = float(match.group(1)), float(match.group(2))
                x_min = min(x_min, current_x)
                x_max = max(x_max, current_x)
                y_min = min(y_min, current_y)
                y_max = max(y_max, current_y)
                continue
            match = g2g3_pattern.match(clean_line)
            if match:
                end_x, end_y = float(match.group(1)), float(match.group(2))
                i, j = float(match.group(3)), float(match.group(4))
                x_min = min(x_min, end_x)
                x_max = max(x_max, end_x)
                y_min = min(y_min, end_y)
                y_max = max(y_max, end_y)
                center_x, center_y = current_x + i, current_y + j
                radius = math.sqrt(i*i + j*j)
                x_min = min(x_min, center_x - radius)
                x_max = max(x_max, center_x + radius)
                y_min = min(y_min, center_y - radius)
                y_max = max(y_max, center_y + radius)
                current_x, current_y = end_x, end_y
        if x_min == float('inf'):
            x_min, y_min = 0.0, 0.0
        if x_max == float('-inf'):
            x_max, y_max = 100.0, 100.0
        return {
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max,
            'width': x_max - x_min,
            'height': y_max - y_min
        }

    def _rescale_gcode(self, lines: List[str], scale: float) -> Tuple[List[str], Dict[str, int]]:
        result = []
        stats = {'g0g1': 0, 'g2g3': 0, 'other': 0}
        g0g1_pattern = re.compile(r'([gG][01]\s+)(.*?)([xX])([\-\d.]+)(.*?)([yY])([\-\d.]+)(.*)')
        g2g3_pattern = re.compile(r'([gG][23]\s+)(.*?)([xX])([\-\d.]+)(.*?)([yY])([\-\d.]+)(.*?)([iI])([\-\d.]+)(.*?)([jJ])([\-\d.]+)(.*)')
        for line in lines:
            clean_line = line.strip()
            match = g0g1_pattern.match(clean_line)
            if match:
                prefix, mid1, x_cmd, x_val, mid2, y_cmd, y_val, suffix = match.groups()
                new_x = float(x_val) * scale
                new_y = float(y_val) * scale
                new_line = f"{prefix}{mid1}{x_cmd}{new_x:.3f}{mid2}{y_cmd}{new_y:.3f}{suffix}\n"
                result.append(new_line)
                stats['g0g1'] += 1
                continue
            match = g2g3_pattern.match(clean_line)
            if match:
                prefix, mid1, x_cmd, x_val, mid2, y_cmd, y_val, mid3, i_cmd, i_val, mid4, j_cmd, j_val, suffix = match.groups()
                new_x = float(x_val) * scale
                new_y = float(y_val) * scale
                new_i = float(i_val) * scale
                new_j = float(j_val) * scale
                new_line = f"{prefix}{mid1}{x_cmd}{new_x:.3f}{mid2}{y_cmd}{new_y:.3f}{mid3}{i_cmd}{new_i:.3f}{mid4}{j_cmd}{new_j:.3f}{suffix}\n"
                result.append(new_line)
                stats['g2g3'] += 1
                continue
            result.append(line)
            stats['other'] += 1
        return result, stats
