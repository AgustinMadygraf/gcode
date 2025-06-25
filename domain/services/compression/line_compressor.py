"""
Compresor para optimizar líneas de G-code consolidando movimientos lineales.
"""
from domain.ports.gcode_compression_port import GcodeCompressionPort
from domain.models.compression_metrics import CompressionMetrics
from typing import List, Tuple
import re

class LineCompressor(GcodeCompressionPort):
    """
    Comprime secuencias de movimientos lineales en la misma coordenada.
    Trabaja directamente con líneas de texto G-code.
    """
    
    def compress(self, gcode_lines: List[str], tolerance: float) -> Tuple[List[str], CompressionMetrics]:
        """
        Comprime líneas de G-code buscando movimientos lineales consecutivos.
        Args:
            gcode_lines: Lista de líneas de G-code a comprimir
            tolerance: Tolerancia para comparar coordenadas
        Returns:
            Tupla (líneas comprimidas, métricas de compresión)
        """
        optimized_lines = []
        i = 0
        segments_removed = 0
        lines_optimized = 0
        
        while i < len(gcode_lines):
            line = gcode_lines[i].strip()
            
            # Preservar comandos de configuración y comentarios
            if not line.startswith('G1 '):
                optimized_lines.append(line)
                i += 1
                continue
            
            # Detectar inicio de una secuencia lineal
            g1_match = re.match(r'G1 X([\d.-]+) Y([\d.-]+)(?: F(\d+))?', line)
            if not g1_match:
                optimized_lines.append(line)
                i += 1
                continue
                
            y_value = float(g1_match.group(2))
            current_y = y_value
            start_x = float(g1_match.group(1))
            feedrate = g1_match.group(3)
            
            # Buscar último punto en esta secuencia Y
            j = i + 1
            sequence_length = 1
            end_x = start_x
            
            while j < len(gcode_lines):
                next_line = gcode_lines[j].strip()
                next_match = re.match(r'G1 X([\d.-]+) Y([\d.-]+)(?: F(\d+))?', next_line)
                
                if next_match and abs(float(next_match.group(2)) - current_y) < tolerance:
                    end_x = float(next_match.group(1))
                    # Actualizar feedrate si está presente
                    if next_match.group(3):
                        feedrate = next_match.group(3)
                    sequence_length += 1
                    j += 1
                else:
                    break
            
            # Si encontramos una secuencia, generar comando optimizado
            if sequence_length > 1:
                feed_part = f" F{feedrate}" if feedrate else ""
                optimized_lines.append(f"G1 X{end_x:.3f} Y{current_y:.3f}{feed_part}")
                segments_removed += sequence_length - 1
                lines_optimized += 1
                i = j
            else:
                optimized_lines.append(line)
                i += 1
        
        metrics = CompressionMetrics(
            original_lines=len(gcode_lines),
            compressed_lines=len(optimized_lines),
            arcs_created=0,
            relative_moves=0,
            redundancies_removed=segments_removed
        )
        
        return optimized_lines, metrics
