"""
Adapter for G-code generation, implementing the GcodeGeneratorPort domain port.
"""
from typing import List, Optional, Any, Dict
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
from infrastructure.transform_manager import TransformManager
from adapters.output.feed_rate_strategy import FeedRateStrategy
from adapters.output.sample_transform_pipeline import SampleTransformPipeline
from adapters.output.gcode_builder_helper import GCodeBuilderHelper
from adapters.output.curvature_feed_calculator import CurvatureFeedCalculator
from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
from domain.services.optimization.trajectory_optimizer import TrajectoryOptimizer
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
        transform_manager: Optional[TransformManagerPort] = None,
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
        self.path_gcode_generator = PathGcodeGenerator(
            self.path_sampler,
            self.transform_manager,
            self.feed_rate_strategy,
            self.cmd_down,
            self.cmd_up
        )

    def calculate_curvature_factor(self, p1, p2, p3, base_feed_rate):
        """
        DEPRECATED: Usar CurvatureFeedCalculator.adjust_feed en su lugar.
        """
        return self.curvature_feed_calculator.adjust_feed(p1, p2, p3)

    def generate_gcode_commands(self, all_points: List[List[Point]], use_relative_moves: bool = False):
        def feed_fn(prev_pt, curr_pt, next_pt, future_pt):
            # Usar CurvatureFeedCalculator para calcular el feed
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

    def generate(self, paths, svg_attr: Dict[str, Any]) -> List[str]:
        gcode = []  # Valor por defecto para evitar UnboundLocalError
        # Log orden y distancia antes de optimizar
        ids = [self._path_id(p, i) for i, p in enumerate(paths)]
        self.logger.debug(self.i18n.get("DEBUG_PATHS_ORDER_ORIG", list=f"{ids[:20]}{'...' if len(ids) > 20 else ''}"))
        self.logger.debug(self.i18n.get("DEBUG_TOTAL_DIST_ORIG", dist=f"{self._total_travel_distance(paths):.2f}"))
        from cli.progress_bar import print_progress_bar
        optimizer = TrajectoryOptimizer()
        def progress_callback(current, total):
            if total > 5:
                percent = int((current / float(total)) * 100) if total else 100
                if not hasattr(progress_callback, '_last_percent') or percent != progress_callback._last_percent:
                    print_progress_bar(current, total, prefix=self.i18n.get('OPTIMIZING_PATHS'), suffix='', length=40, lang=getattr(self.i18n, 'default_lang', 'es'))
                    progress_callback._last_percent = percent
                if current == total:
                    self.logger.debug("Optimización de paths finalizada (barra de progreso completada)")
        optimized_paths = optimizer.optimize_order(paths, progress_callback=progress_callback)
        ids = [self._path_id(p, i) for i, p in enumerate(paths)]
        self.logger.debug(self.i18n.get("DEBUG_PATHS_ORDER_OPT", list=f"{ids[:20]}{'...' if len(ids) > 20 else ''}"))

        self.logger.debug(self.i18n.get("DEBUG_TOTAL_DIST_OPT", dist=f"{self._total_travel_distance(optimized_paths):.2f}"))
        bbox = BoundingBoxCalculator.get_svg_bbox(optimized_paths)

        
        scale = ScaleManager.viewbox_scale(svg_attr)
        scale = ScaleManager.adjust_scale_for_max_height(optimized_paths, scale, self.max_height_mm)
        scale = ScaleManager.adjust_scale_for_max_width(optimized_paths, scale, self.max_width_mm)

        xmin, xmax, ymin, ymax = bbox
        self.logger.debug(self.i18n.get("DEBUG_BOUNDING_BOX", xmin=f"{xmin:.3f}", xmax=f"{xmax:.3f}", ymin=f"{ymin:.3f}", ymax=f"{ymax:.3f}"))
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
        gcode, metrics = self.generate_gcode_commands(all_points, use_relative_moves=use_relative_moves)
        # Compresión configurable
        compression_service = GcodeCompressionFactory.get_compression_service(self.config, logger=self.logger)
        if compression_service:
            from domain.compression_config import CompressionConfig
            compression_config = CompressionConfig()
            gcode, _ = compression_service.compress(gcode, compression_config)
        self.logger.debug(self.i18n.get("DEBUG_GCODE_LINES", count=len(gcode)))
        self.logger.debug(self.i18n.get("DEBUG_OPTIMIZATION_METRICS", metrics=metrics))
        if remove_border:
            detector = GCodeBorderRectangleDetector()
            border_filter = GCodeBorderFilter(detector)
            gcode = border_filter.filter(gcode if isinstance(gcode, str) else '\n'.join(gcode))
            if isinstance(gcode, str):
                gcode = gcode.split('\n')
        return gcode

    def sample_transform_pipeline(self, paths, scale) -> List[List[Point]]:
        pipeline = SampleTransformPipeline(self.path_sampler, self.transform_manager, scale)
        return pipeline.process(paths)

    def generate_path_gcode(self, path, feed, context=None):
        return self.path_gcode_generator.generate(path, context)

    def _generate_single_path(self, points, feed):
        # Deprecated: ahora se usa PathGcodeGenerator
        return self.path_gcode_generator._generate_single_path(points, feed)
