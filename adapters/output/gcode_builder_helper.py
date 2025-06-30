"""
GCodeBuilderHelper: Encapsula la lógica de construcción de comandos G-code a partir de listas de puntos y parámetros de movimiento.
"""
from typing import List, Optional
from domain.entities.point import Point
from domain.gcode.gcode_command_builder import GCodeCommandBuilder
from domain.gcode.commands.arc_command import RelativeMoveCommand

class GCodeBuilderHelper:
    def __init__(self, cmd_down: str, cmd_up: str, dwell_ms: int):
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.dwell_ms = dwell_ms

    def build(self, all_points: List[List[Point]], feed_fn, use_relative_moves: bool = False):
        import math
        TOLERANCIA = 1e-4
        def diferentes(p1, p2):
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            return math.hypot(dx, dy) > TOLERANCIA
        builder = GCodeCommandBuilder()
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
            n = len(points)
            last_feed = None
            for j in range(1, n):
                prev_pt = points[j-2] if j > 1 else None
                curr_pt = points[j-1]
                next_pt = points[j]
                future_pt = points[j+1] if j+1 < n else None
                feed = feed_fn(prev_pt, curr_pt, next_pt, future_pt)
                # Incluir feed en el primer G1 del trazo o si cambia el valor
                feed_to_use = feed if (j == 1 or feed != last_feed) else None
                if use_relative_moves:
                    dx = next_pt.x - curr_pt.x
                    dy = next_pt.y - curr_pt.y
                    builder.commands.append(RelativeMoveCommand(dx, dy, feed=feed_to_use, rapid=False))
                else:
                    builder.move_to(next_pt.x, next_pt.y, feed=feed_to_use, rapid=False)
                last_feed = feed
                last_pos = next_pt
        builder.dwell(self.dwell_ms / 1000.0)
        builder.tool_up(self.cmd_up)
        builder.dwell(self.dwell_ms / 1000.0)
        builder.move_to(0, 0, rapid=True)
        builder.commands.append(type('EndComment', (), {'to_gcode': lambda self: "(End)"})())
        return builder.to_gcode_lines_with_metrics()
