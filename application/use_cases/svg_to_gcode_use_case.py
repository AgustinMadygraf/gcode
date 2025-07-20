"""
Caso de uso: Orquestación completa de conversión SVG → G-code
(procesamiento, generación y compresión).
"""

from pathlib import Path
from domain.services.geometry_rotate import rotate_paths_90_clockwise
from infrastructure.logger_helper import LoggerHelper
from application.use_cases.svgpathtools_rotate import rotate_svgpathtools_paths_90_clockwise

class SvgToGcodeUseCase(LoggerHelper):
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
                 filename_service,
                 i18n=None,
                 config=None):
        super().__init__(config=config, logger=logger)
        self.svg_loader_factory = svg_loader_factory
        self.path_processing_service = path_processing_service
        self.gcode_generation_service = gcode_generation_service
        self.gcode_compression_use_case = gcode_compression_use_case
        self.logger = logger
        self.filename_service = filename_service
        self.i18n = i18n
        self.config = config

    def _load_svg(self, svg_file):
        try:
            svg_loader = self.svg_loader_factory(svg_file)
            paths = svg_loader.get_paths()
            svg_attr = svg_loader.get_attributes()
            self._debug(f"Atributos SVG: {svg_attr}")
            self._debug(f"Paths extraídos: {len(paths)} | Tipo primer path: {type(paths[0]) if paths else 'N/A'}")
            return svg_loader, paths, svg_attr
        except Exception as e:
            self.logger.error(f"Error cargando paths del SVG: {e}", exc_info=True)
            raise

    def _process_paths(self, paths, svg_attr, svg_file, context=None):
        try:
            processed_paths = self.path_processing_service.process(paths, svg_attr, context=context)
            self._debug(self.i18n.get('INFO_PATHS_PROCESSED', count=len(processed_paths)))
            if not processed_paths:
                self.logger.warning(self.i18n.get('WARN_NO_USEFUL_PATHS', filename=svg_file))
            return processed_paths
        except Exception as e:
            self.logger.error(self.i18n.get('ERROR_PROCESSING_PATHS', error=str(e)), exc_info=True)
            raise

    def _generate_gcode(self, processed_paths, svg_attr, context):
        try:
            self._debug(self.i18n.get('DEBUG_GCODE_CONTEXT', context=context))
            # --- Aplicar offset a las coordenadas ---
            offset_x = context.get('offset_x', 0) if context else 0
            offset_y = context.get('offset_y', 0) if context else 0
            if offset_x or offset_y:
                def apply_offset(path):
                    # Aplica offset solo a los dos primeros valores de cada punto
                    return [
                        tuple([p[0] + offset_x, p[1] + offset_y] + list(p[2:])) if isinstance(p, (list, tuple)) and len(p) >= 2 else p
                        for p in path
                    ]
                processed_paths = [apply_offset(path) for path in processed_paths]
                self._debug(f"Offset aplicado: X={offset_x}, Y={offset_y}")
            gcode_lines = self.gcode_generation_service.generate(
                processed_paths,
                svg_attr,
                context=context
            )
            self._debug(self.i18n.get('INFO_GCODE_GENERATED', count=len(gcode_lines)))
            return gcode_lines
        except Exception as e:
            self.logger.error(self.i18n.get('ERROR_GCODE_GENERATION', error=str(e)), exc_info=True)
            raise

    def _compress_gcode(self, gcode_lines, svg_file):
        try:
            compression_result = self.gcode_compression_use_case.execute(gcode_lines)
            compressed_gcode = compression_result.get('compressed_gcode', gcode_lines)
            ratio = compression_result.get('compression_ratio', 1)
            self._debug(self.i18n.get(
                'INFO_COMPRESSION_SUMMARY',
                orig=compression_result.get('original_size', 0),
                comp=compression_result.get('compressed_size', 0),
                ratio=f"{100 * (1 - ratio):.2f}"
            ))
            if ratio > 0.95:
                self._debug(self.i18n.get('WARN_COMPRESSION_LOW', ratio=ratio, filename=svg_file))
            return compressed_gcode, compression_result
        except Exception as e:
            self.logger.error(self.i18n.get('ERROR_GCODE_COMPRESSION', error=str(e)), exc_info=True)
            raise

    def execute(
        self,
        svg_file: Path,
        context: dict = None
    ):
        " Orquesta la conversión de SVG a G-code, incluyendo carga, procesamiento, generación y compresión. "
        self._debug(f"Iniciando carga de SVG: {svg_file}")
        _, paths, svg_attr = self._load_svg(svg_file)
        # Rotar paths si la configuración lo indica
        config = getattr(self, 'config', None)
        rotate_90 = False
        if context and 'config' in context:
            config = context['config']
        if config and hasattr(config, 'rotate_90_clockwise'):
            rotate_90 = config.rotate_90_clockwise
        elif context and 'rotate_90_clockwise' in context:
            rotate_90 = context['rotate_90_clockwise']
        self._debug(f"Flag rotate_90_clockwise: {rotate_90} | Tipo primer path: {type(paths[0]) if paths else 'N/A'}")
        if rotate_90:
            before = str(paths[0]) if paths else 'N/A'
            # Si los paths son de svgpathtools, rotar usando la función específica
            if 'svgpathtools' in str(type(paths[0])):
                paths = rotate_svgpathtools_paths_90_clockwise(paths)
            else:
                paths = rotate_paths_90_clockwise(paths)
            after = str(paths[0]) if paths else 'N/A'
            self._debug(f"Se ejecutó rotación 90°. Antes: {before} | Después: {after}")
        processed_paths = self._process_paths(paths, svg_attr, svg_file, context=context)
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
