"""
Path: adapters/output/gcode_generator_adapter.py
Adapter for G-code generation, implementing the GcodeGeneratorPort domain port.
"""

import time
from typing import List, Optional
from tqdm import tqdm

from domain.entities.point import Point
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.transform_manager_port import TransformManagerPort
from domain.geometry.scale_manager import ScaleManager
from domain.gcode.gcode_border_rectangle_detector import GCodeBorderRectangleDetector
from domain.gcode.gcode_border_filter import GCodeBorderFilter
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from domain.ports.transform_manager_port import NullTransformManager
from domain.services.optimization.trajectory_optimizer import TrajectoryOptimizer
from domain.compression_config import CompressionConfig

from infrastructure.transform_manager import TransformManager
from adapters.output.feed_rate_strategy import FeedRateStrategy
from adapters.output.sample_transform_pipeline import SampleTransformPipeline
from adapters.output.gcode_builder_helper import GCodeBuilderHelper
from adapters.output.curvature_feed_calculator import CurvatureFeedCalculator
from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
from adapters.output.path_gcode_generator import PathGcodeGenerator
from adapters.output.gcode_compression_factory import GcodeCompressionFactory

class GCodeGeneratorAdapter(GcodeGeneratorPort):
    """
    Adapter for G-code generation from SVG paths, implementing the domain port.

    Dependencias inyectadas (puertos):
    - path_sampler: PathSamplerPort
    - feed_rate_strategy: FeedRateStrategy
    - config: ConfigPort
    - logger: LoggerPort
    - transform_strategies: List[PathTransformStrategyPort]
    - optimizer: GcodeOptimizationChainPort
    - transform_manager: TransformManagerPort
    - i18n: objeto de internacionalización (debe implementar .get(key, **kwargs))

    Contratos esperados:
    - Todos los puertos deben implementar los métodos definidos en sus interfaces.
    - Las estrategias de transformación deben ser instancias de PathTransformStrategyPort.
    - El logger debe implementar debug(msg: str) y opcionalmente info/warning/error.
    - El config debe exponer flags como 'curvature_adjustment_factor', 'minimum_feed_factor', 'disable_gcode_compression', etc.
    - El i18n debe proveer mensajes localizables vía get(key, **kwargs).
    """
    def __init__(
        self,
        *,
        path_sampler: PathSamplerPort,
        feed: float,
        cmd_down: str,
        cmd_up: str,
        step_mm: float,
        dwell_ms: int,
        max_height_mm: float,
        max_width_mm: float = 180.0,
        config: ConfigPort,  # Inject config port
        logger: LoggerPort = None,
        transform_strategies: Optional[List[PathTransformStrategyPort]] = None,
        optimizer: Optional[GcodeOptimizationChainPort] = None,
        _transform_manager: Optional[TransformManagerPort] = None,
        i18n=None
    ):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.step_mm = step_mm
        self.dwell_ms = dwell_ms
        self.max_height_mm = max_height_mm
        self.max_width_mm = max_width_mm
        self.logger: LoggerPort = logger
        self.transform_strategies = transform_strategies or []
        if self.transform_strategies:
            for s in self.transform_strategies:
                if not isinstance(s, PathTransformStrategyPort):
                    raise TypeError("Todas las estrategias deben implementar PathTransformStrategy")
        self.path_sampler = path_sampler
        # Usar TransformManager real si hay estrategias, si no NullTransformManager
        if self.transform_strategies:
            self.transform_manager = TransformManager(self.transform_strategies, logger=self.logger)
        else:
            self.transform_manager = NullTransformManager()
        self.optimizer = optimizer
        self.config = config
        self.feed_rate_strategy = FeedRateStrategy(
            base_feed=feed,
            curvature_factor=getattr(config, 'curvature_adjustment_factor', 0.35),
            min_feed_factor=getattr(config, 'minimum_feed_factor', 0.4)
        )
        self.curvature_feed_calculator = CurvatureFeedCalculator(self.feed_rate_strategy)
        self.i18n = i18n
        # Asegura que config tenga i18n para la compresión
        if self.i18n and not hasattr(self.config, 'i18n'):
            setattr(self.config, 'i18n', self.i18n)
        self.path_gcode_generator = PathGcodeGenerator(
            self.path_sampler,
            self.transform_manager,
            self.feed_rate_strategy,
            self.cmd_down,
            self.cmd_up
        )

    def generate_gcode_commands(self, all_points: List[List[Point]], use_relative_moves: bool = False):
        " Genera los comandos G-code a partir de los puntos muestreados y transformados"
        def feed_fn(prev_pt, curr_pt, next_pt, future_pt):
            " Calcula el feed rate basado en la curvatura entre puntos"
            feed = self.curvature_feed_calculator.adjust_feed(prev_pt, curr_pt, next_pt)
            if future_pt is not None:
                future_feed = self.curvature_feed_calculator.adjust_feed(curr_pt, next_pt, future_pt)
                feed = min(feed, future_feed)
            return feed
        builder_helper = GCodeBuilderHelper(self.cmd_down, self.cmd_up, self.dwell_ms)
        return builder_helper.build(all_points, feed_fn, use_relative_moves=use_relative_moves)

    def _path_id(self, path, idx):
        # Devuelve un identificador legible para logs
        return getattr(path, 'id', f'path_{idx}')

    def _total_travel_distance(self, paths):
        # Calcula la distancia total "en el aire" entre el final de un path y el inicio del siguiente
        if not paths:
            return 0.0
        dist = 0.0
        for i in range(len(paths) - 1):
            end_pt = getattr(paths[i], 'end_point', None)
            start_pt = getattr(paths[i+1], 'start_point', None)
            if end_pt and start_pt:
                dist += ((end_pt.x - start_pt.x)**2 + (end_pt.y - start_pt.y)**2) ** 0.5
        return dist

    def generate(self, paths, svg_attr: dict, context=None) -> list:  # pylint: disable=unused-argument
        """
        Genera las líneas de G-code a partir de los paths y atributos SVG.
        El parámetro context permite pasar información adicional (por ejemplo, tool_diameter).
        """
        t_start = time.time()
        # Loguear inicio del proceso de generación de G-code
        self.logger.info(self.i18n.get("INFO_START_GCODE_GEN", count=len(paths), file=svg_attr.get("filename", "N/A")))

        # Validaciones de configuración
        if self.step_mm <= 0:
            self.logger.warning(self.i18n.get("WARN_STEP_MM_INVALID", value=self.step_mm))
        if not self.path_sampler:
            self.logger.error(self.i18n.get("ERR_MISSING_PATH_SAMPLER"))
            raise ValueError("PathSamplerPort is required")
        gcode = []  # Valor por defecto para evitar UnboundLocalError
        # Log orden y distancia antes de optimizar
        ids = [self._path_id(p, i) for i, p in enumerate(paths)]
        self.logger.debug(self.i18n.get("DEBUG_PATHS_ORDER_ORIG", list=f"{ids[:20]}{'...' if len(ids) > 20 else ''}"))
        self.logger.debug(self.i18n.get("DEBUG_TOTAL_DIST_ORIG", dist=f"{self._total_travel_distance(paths):.2f}"))
        optimizer = TrajectoryOptimizer()
        # Loguear inicio de optimización
        self.logger.debug(self.i18n.get("INFO_OPTIMIZING_PATHS"))
        # Barra de progreso con tqdm para optimización
        use_tqdm = True
        pbar = None
        def progress_callback(current, total):
            nonlocal pbar
            if use_tqdm:
                if pbar is None and total > 0:
                    pbar = tqdm(total=total, desc=self.i18n.get('OPTIMIZING_PATHS'), ncols=60)
                if pbar is not None:
                    pbar.n = current
                    pbar.refresh()
                    if current == total:
                        pbar.n = total
                        pbar.refresh()
                        pbar.close()
                        pbar = None
            else:
                percent = int((current / float(total)) * 100) if total else 100
                print(f"Progreso: {percent}%")
        # Usar barra de progreso con tqdm
        optimized_paths = optimizer.optimize_order(paths, progress_callback=progress_callback)
        if pbar is not None and not pbar.disable:
            pbar.close()
        # Loguear si la optimización no tuvo efecto
        if not optimized_paths or optimized_paths == paths:
            self.logger.warning(self.i18n.get("WARN_NO_OPTIMIZATION"))
        ids = [self._path_id(p, i) for i, p in enumerate(paths)]
        self.logger.debug(self.i18n.get("DEBUG_PATHS_ORDER_OPT", list=f"{ids[:20]}{'...' if len(ids) > 20 else ''}"))

        self.logger.debug(self.i18n.get("DEBUG_TOTAL_DIST_OPT", dist=f"{self._total_travel_distance(optimized_paths):.2f}"))
        bbox = BoundingBoxCalculator.get_svg_bbox(optimized_paths)

        scale_original = ScaleManager.viewbox_scale(svg_attr)
        scale = scale_original
        scale = ScaleManager.adjust_scale_for_max_height(optimized_paths, scale, self.max_height_mm)
        scale = ScaleManager.adjust_scale_for_max_width(optimized_paths, scale, self.max_width_mm)
        if scale < scale_original:
            self.logger.debug(self.i18n.get("WARN_SCALE_REDUCED", scale=scale))

        xmin, xmax, ymin, ymax = bbox
        self.logger.debug(
            self.i18n.get(
                "DEBUG_BOUNDING_BOX",
                xmin=f"{xmin:.3f}",
                xmax=f"{xmax:.3f}",
                ymin=f"{ymin:.3f}",
                ymax=f"{ymax:.3f}"
            )
        )
        self.logger.debug(self.i18n.get("DEBUG_SCALE_APPLIED", scale=f"{scale:.3f}"))

        remove_border = GcodeGenerationConfigHelper.get_remove_border(self.config)
        self.logger.debug(self.i18n.get("DEBUG_REMOVE_BORDER", enabled=remove_border))

        use_relative_moves = GcodeGenerationConfigHelper.get_use_relative_moves(self.config)
        self.logger.debug(self.i18n.get("DEBUG_RELATIVE_MOVES", enabled=use_relative_moves))

        bbox = BoundingBoxCalculator.get_svg_bbox(optimized_paths)
        scale = ScaleManager.viewbox_scale(svg_attr)
        scale = ScaleManager.adjust_scale_for_max_height(optimized_paths, scale, self.max_height_mm)
        scale = ScaleManager.adjust_scale_for_max_width(optimized_paths, scale, self.max_width_mm)
        remove_border = GcodeGenerationConfigHelper.get_remove_border(self.config)
        all_points = self.sample_transform_pipeline(optimized_paths, scale)
        try:
            gcode, metrics = self.generate_gcode_commands(all_points, use_relative_moves=use_relative_moves)
        except Exception:
            self.logger.exception(self.i18n.get("ERR_GCODE_BUILD_FAILED"))
            raise
        compression_service = GcodeCompressionFactory.get_compression_service(
            self.config,
            logger=self.logger
        )
        if compression_service:
            compression_config = CompressionConfig()
            orig_len = len(gcode)
            gcode, _ = compression_service.compress(gcode, compression_config)
            reduction = 100 * (1 - len(gcode) / orig_len) if orig_len else 0
            self.logger.debug(self.i18n.get("INFO_COMPRESSION", reduction=f"{reduction:.1f}%"))
        self.logger.debug(self.i18n.get("DEBUG_GCODE_LINES", count=len(gcode)))
        self.logger.debug(self.i18n.get("DEBUG_OPTIMIZATION_METRICS", metrics=metrics))
        if remove_border:
            detector = GCodeBorderRectangleDetector()
            border_filter = GCodeBorderFilter(detector)
            # Detectar borde antes de filtrar
            gcode_str = (
                gcode if isinstance(gcode, str)
                else '\n'.join(gcode)
            )
            border_found = detector.detect_border_pattern(
                gcode_str
            )
            if not border_found:
                self.logger.debug(self.i18n.get("WARN_BORDER_NOT_FOUND"))
            gcode = border_filter.filter(gcode if isinstance(gcode, str) else '\n'.join(gcode))
            if isinstance(gcode, str):
                gcode = gcode.split('\n')
        elapsed_ms = int((time.time() - t_start) * 1000)
        self.logger.debug(self.i18n.get("INFO_GCODE_READY", ms=elapsed_ms, lines=len(gcode)))
        return gcode

    def sample_transform_pipeline(self, paths, scale) -> List[List[Point]]:
        " Aplica el pipeline de muestreo y transformación a los paths"
        pipeline = SampleTransformPipeline(self.path_sampler, self.transform_manager, scale)
        return pipeline.process(paths)
