"""
Caso de uso para reescalar archivos GCODE manteniendo su relación de aspecto.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import re
import math

class GcodeRescaleUseCase:
    def __init__(self, filename_service, logger=None, config_provider=None):
        self.filename_service = filename_service
        self.logger = logger
        self.config = config_provider

    def execute(self, gcode_file: Path, target_height: Optional[float] = None) -> Dict[str, Any]:
        if self.logger:
            self.logger.info(f"Reescalando archivo GCODE: {gcode_file}")
        with open(gcode_file, 'r') as f:
            lines = f.readlines()
        dimensions = self._analyze_dimensions(lines)
        current_width = dimensions['width']
        current_height = dimensions['height']
        max_height = target_height or self._get_max_height_from_config()
        scale_factor = max_height / current_height if current_height else 1.0
        scaled_lines, rescale_stats = self._rescale_gcode(lines, scale_factor, dimensions)
        # Generar nombre de archivo de salida manualmente
        output_dir = self.config.get_gcode_output_dir() if self.config else gcode_file.parent
        stem = gcode_file.stem
        scale_tag = f"_scaled_{int(current_width * scale_factor)}x{int(current_height * scale_factor)}"
        candidate = output_dir / f"{stem}{scale_tag}.gcode"
        # Evitar sobrescribir archivos existentes
        idx = 0
        final_candidate = candidate
        while final_candidate.exists():
            final_candidate = output_dir / f"{stem}{scale_tag}_v{idx:02d}.gcode"
            idx += 1
        output_file = final_candidate
        with open(output_file, 'w') as f:
            f.write(''.join(scaled_lines))
        return {
            'output_file': output_file,
            'original_dimensions': dimensions,
            'new_dimensions': {
                'width': current_width * scale_factor,
                'height': current_height * scale_factor,
                'x_min': dimensions['x_min'] * scale_factor,
                'x_max': dimensions['x_max'] * scale_factor,
                'y_min': dimensions['y_min'] * scale_factor,
                'y_max': dimensions['y_max'] * scale_factor
            },
            'scale_factor': scale_factor,
            'commands_rescaled': rescale_stats
        }

    def _get_max_height_from_config(self) -> float:
        if self.config and hasattr(self.config, 'max_height_mm'):
            return getattr(self.config, 'max_height_mm', 250.0)
        return 250.0

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

    def _rescale_gcode(self, lines: List[str], scale: float, dimensions: Dict[str, float]) -> Tuple[List[str], Dict[str, int]]:
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
