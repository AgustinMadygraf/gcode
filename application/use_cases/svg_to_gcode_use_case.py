"""
Caso de uso: Orquestación completa de conversión SVG → G-code
(procesamiento, generación y compresión).
"""
from pathlib import Path

class SvgToGcodeUseCase:
    """
    Orquesta la conversión de SVG a G-code, incluyendo carga, 
    procesamiento, generación y compresión.
    """
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

    def execute(
        self,
        svg_file: Path,
        context: dict = None
    ):
        (
            " Orquesta la conversión de SVG a "
            "G-code. "
        )
        self.logger.debug(f"Iniciando carga de SVG: {svg_file}")
        _, paths, svg_attr = self._load_svg(svg_file)
        processed_paths = self._process_paths(paths, svg_attr, svg_file)
        gcode_lines = self._generate_gcode(processed_paths, svg_attr, context)
        compressed_gcode, compression_result = self._compress_gcode(gcode_lines, svg_file)
        return {
            'svg_file': svg_file,
            'svg_attr': svg_attr,
            'processed_paths': processed_paths,
            'gcode_lines': gcode_lines,
            'compressed_gcode': compressed_gcode,
            'compression_result': compression_result
        }

    def _load_svg(self, svg_file):
        try:
            svg_loader = self.svg_loader_factory(svg_file)
            paths = svg_loader.get_paths()
            svg_attr = svg_loader.get_attributes()
            self.logger.debug(f"Atributos SVG: {svg_attr}")
            self.logger.info(f"Paths extraídos: {len(paths)}")
            return svg_loader, paths, svg_attr
        except Exception as e:
            self.logger.error(f"Error al cargar SVG o extraer paths: {e}", exc_info=True)
            raise

    def _process_paths(self, paths, svg_attr, svg_file):
        try:
            processed_paths = self.path_processing_service.process(paths, svg_attr)
            self.logger.info(f"Paths útiles tras procesamiento: {len(processed_paths)}")
            if not processed_paths:
                self.logger.warning(
                    "No se encontraron paths útiles tras el "
                    "procesamiento para "
                    f"{svg_file}"
                )
            return processed_paths
        except Exception as e:
            self.logger.error(f"Error en el procesamiento de paths: {e}", exc_info=True)
            raise

    def _generate_gcode(self, processed_paths, svg_attr, context):
        try:
            self.logger.debug(f"Contexto para generación de G-code: {context}")
            gcode_lines = self.gcode_generation_service.generate(
                processed_paths,
                svg_attr,
                context=context
            )
            self.logger.info(
                f"G-code generado con {len(gcode_lines)} líneas"
            )
            return gcode_lines
        except Exception as e:
            self.logger.error(f"Error en la generación de G-code: {e}", exc_info=True)
            raise

    def _compress_gcode(self, gcode_lines, svg_file):
        try:
            compression_result = self.gcode_compression_use_case.execute(gcode_lines)
            compressed_gcode = compression_result.get('compressed_gcode', gcode_lines)
            ratio = compression_result.get('compression_ratio', 1)
            self.logger.info(
                f"Compresión: original={compression_result.get('original_size', 0)}, "
                f"comprimido={compression_result.get('compressed_size', 0)}, "
                f"ratio={100 * (1 - ratio):.2f}%"
            )
            if ratio > 0.95:
                self.logger.warning(
                    f"La compresión fue poco efectiva "
                    f"(ratio={ratio:.2f}) para {svg_file}"
                )
            return compressed_gcode, compression_result
        except Exception as e:
            self.logger.error(f"Error en la compresión de G-code: {e}", exc_info=True)
            raise
