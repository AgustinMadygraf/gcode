# Este archivo fue movido a domain/services/optimization/arc_optimizer.py
from typing import List, Dict, Any
from domain.ports.gcode_optimization_port import GcodeOptimizationPort
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.arc_command import ArcCommand
from domain.gcode.commands.move_command import MoveCommand
import math

class ArcOptimizer(GcodeOptimizationPort):
    """Detecta secuencias de movimientos que pueden representarse como arcos y las reemplaza por ArcCommand."""
    def __init__(self, tolerance=0.1, min_points=3):
        self.tolerance = tolerance
        self.min_points = min_points

    def optimize(self, commands: List[BaseCommand], tolerance: float = None) -> tuple[List[BaseCommand], Dict[str, Any]]:
        result = []
        i = 0
        arcs_found = 0
        tol = tolerance if tolerance is not None else self.tolerance
        while i < len(commands):
            if (
                isinstance(commands[i], MoveCommand)
                and not commands[i].rapid
            ):
                arc_seq = [commands[i]]
                j = i + 1
                while (
                    j < len(commands)
                    and isinstance(commands[j], MoveCommand)
                    and not commands[j].rapid
                ):
                    arc_seq.append(commands[j])
                    j += 1
                if len(arc_seq) >= self.min_points:
                    arc = self._fit_arc(arc_seq, tol)
                    if arc:
                        result.append(arc)
                        arcs_found += 1
                        i = j
                        continue
                result.extend(arc_seq)
                i = j
            else:
                result.append(commands[i])
                i += 1
        metrics = {"arcs_found": arcs_found}
        return result, metrics

    def _fit_arc(self, moves: List[MoveCommand], tolerance: float):
        if len(moves) != 3:
            return None
        p1, p2, p3 = moves[0], moves[1], moves[2]
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        temp = x2**2 + y2**2
        bc = (x1**2 + y1**2 - temp) / 2.0
        cd = (temp - x3**2 - y3**2) / 2.0
        det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)
        if abs(det) < 1e-6:
            return None
        cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
        cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
        r = math.hypot(x1 - cx, y1 - cy)
        for p in [p1, p2, p3]:
            if abs(math.hypot(p.x - cx, p.y - cy) - r) > tolerance:
                return None
        i = cx - x1
        j = cy - y1
        clockwise = ((x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)) < 0
        return ArcCommand(x3, y3, i, j, clockwise, feed=p1.feed)
