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
from domain.gcode.gcode_command_builder import GCodeCommandBuilder
from domain.gcode.gcode_border_rectangle_detector import GCodeBorderRectangleDetector
from domain.gcode.gcode_border_filter import GCodeBorderFilter
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.gcode.commands.arc_command import RelativeMoveCommand
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from domain.ports.transform_manager_port import NullTransformManager
from infrastructure.transform_manager import TransformManager
from adapters.output.feed_rate_strategy import FeedRateStrategy
from adapters.output.sample_transform_pipeline import SampleTransformPipeline
from adapters.output.gcode_builder_helper import GCodeBuilderHelper

class GCodeGeneratorAdapter(GcodeGeneratorPort):
    """Adapter for G-code generation from SVG paths, implementing the domain port."""
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
        transform_manager: Optional[TransformManagerPort] = None
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

    def calculate_curvature_factor(self, p1, p2, p3, base_feed_rate):
        """
        DEPRECATED: Usar FeedRateStrategy.adjust_feed en su lugar.
        """
        import math
        if p1 is None or p2 is None or p3 is None:
            return base_feed_rate
        v1 = (p2.x - p1.x, p2.y - p1.y)
        v2 = (p3.x - p2.x, p3.y - p2.y)
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 < 1e-6 or mag2 < 1e-6:
            return base_feed_rate
        dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)
        angle_deg = math.degrees(angle)
        curvature = angle_deg / 180
        return self.feed_rate_strategy.adjust_feed(curvature=curvature)

    def generate_gcode_commands(self, all_points: List[List[Point]], use_relative_moves: bool = False):
        def feed_fn(prev_pt, curr_pt, next_pt, future_pt):
            # Usar FeedRateStrategy para calcular el feed
            curvature = None
            if prev_pt and curr_pt and next_pt:
                import math
                v1 = (curr_pt.x - prev_pt.x, curr_pt.y - prev_pt.y)
                v2 = (next_pt.x - curr_pt.x, next_pt.y - curr_pt.y)
                mag1 = math.hypot(*v1)
                mag2 = math.hypot(*v2)
                if mag1 > 1e-6 and mag2 > 1e-6:
                    dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
                    dot = max(-1.0, min(1.0, dot))
                    angle = math.acos(dot)
                    angle_deg = math.degrees(angle)
                    curvature = angle_deg / 180
            feed = self.feed_rate_strategy.adjust_feed(curvature=curvature)
            if future_pt is not None:
                future_curvature = None
                if curr_pt and next_pt and future_pt:
                    v1 = (next_pt.x - curr_pt.x, next_pt.y - curr_pt.y)
                    v2 = (future_pt.x - next_pt.x, future_pt.y - next_pt.y)
                    mag1 = math.hypot(*v1)
                    mag2 = math.hypot(*v2)
                    if mag1 > 1e-6 and mag2 > 1e-6:
                        dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
                        dot = max(-1.0, min(1.0, dot))
                        angle = math.acos(dot)
                        angle_deg = math.degrees(angle)
                        future_curvature = angle_deg / 180
                future_feed = self.feed_rate_strategy.adjust_feed(curvature=future_curvature)
                feed = min(feed, future_feed)
            return feed
        builder_helper = GCodeBuilderHelper(self.cmd_down, self.cmd_up, self.dwell_ms)
        return builder_helper.build(all_points, feed_fn, use_relative_moves=use_relative_moves)

    def generate(self, paths, svg_attr: Dict[str, Any]) -> List[str]:
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        xmin, xmax, ymin, ymax = bbox
        scale = ScaleManager.viewbox_scale(svg_attr)
        scale = ScaleManager.adjust_scale_for_max_height(paths, scale, self.max_height_mm)
        scale = ScaleManager.adjust_scale_for_max_width(paths, scale, self.max_width_mm)
        if self.logger:
            self.logger.info(
                f"Bounding box: xmin={xmin:.3f}, xmax={xmax:.3f}, "
                f"ymin={ymin:.3f}, ymax={ymax:.3f}")
            self.logger.info(f"Scale applied: {scale:.3f}")
        try:
            remove_border = self.config.get("REMOVE_BORDER_RECTANGLE", True)
            use_relative_moves = False
            if hasattr(self.config, '_data') and "COMPRESSION" in self.config._data:
                use_relative_moves = self.config._data["COMPRESSION"].get("USE_RELATIVE_MOVES", False)
            else:
                use_relative_moves = self.config.get("USE_RELATIVE_MOVES", False)
        except Exception:
            remove_border = True
            use_relative_moves = False
        if self.logger:
            self.logger.info(f"Relative moves enabled: {use_relative_moves}")
        all_points = self.sample_transform_pipeline(paths, scale)
        gcode, metrics = self.generate_gcode_commands(all_points, use_relative_moves=use_relative_moves)
        if self.logger:
            self.logger.info(f"G-code lines generated: {len(gcode)}")
            self.logger.info(f"Métricas de optimización: {metrics}")
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
        context = context or {}
        tool_type = context.get("tool_type", "pen")
        double_pass = context.get("double_pass", False)
        # Ajustar velocidad según la herramienta usando FeedRateStrategy
        feed = self.feed_rate_strategy.adjust_feed(tool_type=tool_type)
        # Generar puntos para el path
        points = []
        for pt in self.path_sampler.sample(path):
            x, y = self.transform_manager.apply(pt.x, pt.y)
            points.append(Point(x, y))
        gcode_lines = self._generate_single_path(points, feed)
        # Si es lapicera y doble pasada, agregar el trazo inverso
        if tool_type == "pen" and double_pass:
            reverse_points = list(reversed(points))
            gcode_lines += self._generate_single_path(reverse_points, feed)
        return gcode_lines

    def _generate_single_path(self, points, feed):
        # Implementación simplificada para generar G-code de un solo path
        builder = GCodeCommandBuilder()
        if not points:
            return []
        builder.move_to(points[0].x, points[0].y, rapid=True)
        builder.tool_down(self.cmd_down)
        for pt in points[1:]:
            builder.move_to(pt.x, pt.y, feed=feed, rapid=False)
        builder.tool_up(self.cmd_up)
        return builder.to_gcode_lines_with_metrics()[0] if hasattr(builder, 'to_gcode_lines_with_metrics') else builder.to_gcode_lines()
