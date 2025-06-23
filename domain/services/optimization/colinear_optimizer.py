from typing import List, Dict, Any
from domain.ports.gcode_optimization_port import GcodeOptimizationPort
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.move_command import MoveCommand

class ColinearOptimizer(GcodeOptimizationPort):
    """Optimiza secuencias de MoveCommand colineales."""
    def optimize(self, commands: List[BaseCommand], tolerance: float = 0.01) -> tuple[List[BaseCommand], Dict[str, Any]]:
        optimized_cmds = []
        i = 0
        lines_saved = 0
        while i < len(commands):
            cmd = commands[i]
            if (
                isinstance(cmd, MoveCommand)
                and not cmd.rapid
                and i + 1 < len(commands)
            ):
                start = i
                points = [(cmd.x, cmd.y)]
                feed = cmd.feed
                j = i + 1
                while (
                    j < len(commands)
                    and isinstance(commands[j], MoveCommand)
                    and not commands[j].rapid
                ):
                    points.append((commands[j].x, commands[j].y))
                    j += 1
                if len(points) >= 3:
                    optimized_points = [points[0]]
                    dx_prev = points[1][0] - points[0][0]
                    dy_prev = points[1][1] - points[0][1]
                    for k in range(2, len(points)):
                        dx = points[k][0] - points[k-1][0]
                        dy = points[k][1] - points[k-1][1]
                        # Usar tolerancia para colinealidad
                        if abs(dx * dy_prev - dy * dx_prev) > tolerance:
                            optimized_points.append(points[k-1])
                            dx_prev = dx
                            dy_prev = dy
                    optimized_points.append(points[-1])
                    lines_saved += len(points) - len(optimized_points)
                    for idx, (x, y) in enumerate(optimized_points):
                        optimized_cmds.append(MoveCommand(x, y, feed if idx == 0 else None, rapid=False))
                else:
                    for k in range(start, j):
                        optimized_cmds.append(commands[k])
                i = j
            else:
                optimized_cmds.append(cmd)
                i += 1
        metrics = {"lines_saved": lines_saved}
        return optimized_cmds, metrics
