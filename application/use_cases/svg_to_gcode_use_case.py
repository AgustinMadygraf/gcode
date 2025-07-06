"""
Caso de uso: Orquestación completa de conversión SVG → G-code
(procesamiento, generación y compresión).
"""

from pathlib import Path
from domain.services.geometry_rotate import rotate_paths_90_clockwise

class SvgToGcodeUseCase:
    """
    Orquesta la conversión de SVG a G-code, incluyendo carga, 
    procesamiento, generación y compresión.
    """
    DEBUG_ENABLED = False

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def __init__(self, *,
                 svg_loader_factory,
                 path_processing_service,
                 gcode_generation_service,
                 gcode_compression_use_case,
                 logger,
                 filename_service,
                 i18n=None):
        self.svg_loader_factory = svg_loader_factory
        self.path_processing_service = path_processing_service
        self.gcode_generation_service = gcode_generation_service
        self.gcode_compression_use_case = gcode_compression_use_case
        self.logger = logger
        self.filename_service = filename_service
        self.i18n = i18n

    def _load_svg(self, svg_file):
        try:
            svg_loader = self.svg_loader_factory(svg_file)
            paths = svg_loader.get_paths()
            svg_attr = svg_loader.get_attributes()
            self._debug(self.i18n.get('DEBUG_SVG_ATTR', attr=svg_attr))
            self._debug(self.i18n.get('INFO_PATHS_EXTRACTED', count=len(paths)))
            return svg_loader, paths, svg_attr
        except Exception as e:
            self.logger.error(self.i18n.get('ERROR_LOADING_SVG_PATHS', error=str(e)), exc_info=True)
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
        (
            " Orquesta la conversión de SVG a "
            "G-code. "
        )
        self._debug(self.i18n.get('DEBUG_LOADING_SVG', filename=svg_file))
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
        if rotate_90:
            paths = rotate_paths_90_clockwise(paths)
            self._debug('INFO_PATHS_ROTATED_90_CLOCKWISE')
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
