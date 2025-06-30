"""
PathGcodeGenerator: Encapsula la generación de G-code para un path, incluyendo lógica de doble pasada y ajuste de feed.
"""
from typing import Any, List
from domain.entities.point import Point
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.transform_manager_port import TransformManagerPort
from adapters.output.feed_rate_strategy import FeedRateStrategy
from domain.gcode.gcode_command_builder import GCodeCommandBuilder

class PathGcodeGenerator:
    def __init__(self, path_sampler: PathSamplerPort, transform_manager: TransformManagerPort, feed_rate_strategy: FeedRateStrategy, cmd_down: str, cmd_up: str):
        self.path_sampler = path_sampler
        self.transform_manager = transform_manager
        self.feed_rate_strategy = feed_rate_strategy
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up

    def generate(self, path, context: dict = None) -> List[str]:
        context = context or {}
        tool_type = context.get("tool_type", "pen")
        double_pass = context.get("double_pass", False)
        feed = self.feed_rate_strategy.adjust_feed(tool_type=tool_type)
        points = []
        for pt in self.path_sampler.sample(path):
            x, y = self.transform_manager.apply(pt.x, pt.y)
            points.append(Point(x, y))
        gcode_lines = self._generate_single_path(points, feed)
        if tool_type == "pen" and double_pass:
            reverse_points = list(reversed(points))
            gcode_lines += self._generate_single_path(reverse_points, feed)
        return gcode_lines

    def _generate_single_path(self, points: List[Point], feed: float) -> List[str]:
        builder = GCodeCommandBuilder()
        if not points:
            return []
        builder.move_to(points[0].x, points[0].y, rapid=True)
        builder.tool_down(self.cmd_down)
        for pt in points[1:]:
            builder.move_to(pt.x, pt.y, feed=feed, rapid=False)
        builder.tool_up(self.cmd_up)
        return builder.to_gcode_lines_with_metrics()[0] if hasattr(builder, 'to_gcode_lines_with_metrics') else builder.to_gcode_lines()
