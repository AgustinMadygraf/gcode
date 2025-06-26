"""
Caso de uso: Orquestación completa de conversión SVG → G-code (procesamiento, generación y compresión).
"""
from pathlib import Path
from typing import Any, List

class SvgToGcodeUseCase:
    def __init__(self, *,
                 svg_loader_factory,
                 path_processing_service,
                 gcode_generation_service,
                 gcode_compression_use_case,
                 logger,
                 filename_service):
        self.svg_loader_factory = svg_loader_factory
        self.path_processing_service = path_processing_service
        self.gcode_generation_service = gcode_generation_service
        self.gcode_compression_use_case = gcode_compression_use_case
        self.logger = logger
        self.filename_service = filename_service

    def execute(self, svg_file: Path, transform_strategies: List[Any] = None, context: dict = None):
        self.logger.info(f"Carga de SVG: {svg_file}")
        svg_loader = self.svg_loader_factory(svg_file)
        paths = svg_loader.get_paths()
        svg_attr = svg_loader.get_attributes()
        self.logger.info(f"Paths extraídos: {len(paths)}")
        # Procesamiento de paths
        processed_paths = self.path_processing_service.process(paths, svg_attr)
        self.logger.info(f"Paths útiles tras procesamiento: {len(processed_paths)}")
        # Generación de G-code
        gcode_lines = self.gcode_generation_service.generate(processed_paths, svg_attr, context=context)
        self.logger.info(f"G-code generado con {len(gcode_lines)} líneas")
        # Compresión de G-code
        compression_result = self.gcode_compression_use_case.execute(gcode_lines)
        compressed_gcode = compression_result.get('compressed_gcode', gcode_lines)
        self.logger.info(f"Compresión: original={compression_result.get('original_size', 0)}, comprimido={compression_result.get('compressed_size', 0)}, ratio={100 * (1 - compression_result.get('compression_ratio', 1)):.2f}%")
        return {
            'svg_file': svg_file,
            'svg_attr': svg_attr,
            'processed_paths': processed_paths,
            'gcode_lines': gcode_lines,
            'compressed_gcode': compressed_gcode,
            'compression_result': compression_result
        }
