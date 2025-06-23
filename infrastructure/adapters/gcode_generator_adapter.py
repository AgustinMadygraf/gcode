"""
Adaptador para generación de G-code, implementando el puerto de dominio GcodeGeneratorPort.
"""
from typing import List, Optional, Any, Dict
from domain.entities.point import Point
from domain.path_transform_strategy import PathTransformStrategy, ScaleStrategy
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator
from domain.ports.path_sampler_port import IPathSampler
from infrastructure.transform_manager import TransformManager
from domain.geometry.scale_manager import ScaleManager
from domain.gcode.gcode_command_builder import GCodeCommandBuilder
from domain.gcode.gcode_border_rectangle_detector import GCodeBorderRectangleDetector
from domain.gcode.gcode_border_filter import GCodeBorderFilter
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.gcode.commands.arc_command import RelativeMoveCommand
from domain.ports.gcode_generator_port import GcodeGeneratorPort

class GCodeGeneratorAdapter(GcodeGeneratorPort):
    """Adaptador para generación de G-code desde paths SVG, implementando el puerto de dominio."""
    def __init__(
        self,
        *,
        path_sampler: IPathSampler,
        feed: float,
        cmd_down: str,
        cmd_up: str,
        step_mm: float,
        dwell_ms: int,
        max_height_mm: float,
        max_width_mm: float = 180.0,
        logger=None,
        transform_strategies: Optional[List[PathTransformStrategy]] = None,
        optimizer: Optional[GcodeOptimizationChainPort] = None
    ):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.step_mm = step_mm
        self.dwell_ms = dwell_ms
        self.max_height_mm = max_height_mm
        self.max_width_mm = max_width_mm
        self.logger = logger
        self.transform_strategies = transform_strategies or []
        if self.transform_strategies:
            for s in self.transform_strategies:
                if not isinstance(s, PathTransformStrategy):
                    raise TypeError("Todas las estrategias deben implementar PathTransformStrategy")
        self.path_sampler = path_sampler
        self.transform_manager = TransformManager(self.transform_strategies, logger=self.logger)
        self.optimizer = optimizer

    def generate_gcode_commands(self, all_points: List[List[Point]], use_relative_moves: bool = False):
        import math
        TOLERANCIA = 1e-4
        def diferentes(p1, p2):
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            return math.hypot(dx, dy) > TOLERANCIA
        def apply_optimizers(cmds):
            if self.optimizer:
                return self.optimizer.optimize(cmds)
            return cmds, {}
        builder = GCodeCommandBuilder(optimizer=apply_optimizers)
        builder.move_to(0, 0, rapid=True)
        builder.dwell(self.dwell_ms / 1000.0)
        last_pos = Point(0, 0)
        for i, points in enumerate(all_points):
            if not points:
                continue
            dedup_points = [points[0]]
            for j in range(1, len(points)):
                if diferentes(points[j], points[j-1]):
                    dedup_points.append(points[j])
            points = dedup_points
            if i > 0:
                builder.dwell(self.dwell_ms / 1000.0)
                builder.tool_up(self.cmd_up)
                builder.dwell(self.dwell_ms / 1000.0)
            if diferentes(last_pos, points[0]):
                if use_relative_moves:
                    dx = points[0].x - last_pos.x
                    dy = points[0].y - last_pos.y
                    builder.commands.append(RelativeMoveCommand(dx, dy, rapid=True))
                else:
                    builder.move_to(points[0].x, points[0].y, rapid=True)
                last_pos = points[0]
            builder.dwell(self.dwell_ms / 1000.0)
            builder.tool_down(self.cmd_down)
            builder.dwell(self.dwell_ms / 1000.0)
            for pt in points[1:]:
                if use_relative_moves:
                    dx = pt.x - last_pos.x
                    dy = pt.y - last_pos.y
                    builder.commands.append(RelativeMoveCommand(dx, dy, feed=self.feed, rapid=False))
                else:
                    builder.move_to(pt.x, pt.y, feed=self.feed, rapid=False)
                last_pos = pt
        builder.dwell(self.dwell_ms / 1000.0)
        builder.tool_up(self.cmd_up)
        builder.dwell(self.dwell_ms / 1000.0)
        builder.move_to(0, 0, rapid=True)
        builder.commands.append(type('EndComment', (), {'to_gcode': lambda self: "(End)"})())
        return builder.to_gcode_lines_with_metrics()

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
            from config.config import Config
            config = Config()
            remove_border = config.get("REMOVE_BORDER_RECTANGLE", True)
            use_relative_moves = False
            if "COMPRESSION" in config._data:
                use_relative_moves = config._data["COMPRESSION"].get("USE_RELATIVE_MOVES", False)
            else:
                use_relative_moves = config.get("USE_RELATIVE_MOVES", False)
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
        result = []
        for p in paths:
            points = []
            for pt in self.path_sampler.sample(p):
                x, y = self.transform_manager.apply(pt.x, pt.y)
                if not any(isinstance(s, ScaleStrategy) for s in self.transform_strategies):
                    x, y = x * scale, y * scale
                points.append(Point(x, y))
            result.append(points)
        return result
