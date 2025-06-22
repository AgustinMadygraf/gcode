"""
GCodeOptimizer: Interfaz para optimizadores de comandos G-code (Chain of Responsibility).
"""
from abc import ABC, abstractmethod
from typing import List
from domain.gcode.commands.base_command import BaseCommand

class GCodeOptimizer(ABC):
    def __init__(self):
        self._next = None

    def set_next(self, next_optimizer: 'GCodeOptimizer') -> 'GCodeOptimizer':
        self._next = next_optimizer
        return next_optimizer

    @abstractmethod
    def optimize(self, commands: List[BaseCommand]) -> List[BaseCommand]:
        pass

    def _call_next(self, commands: List[BaseCommand]) -> List[BaseCommand]:
        if self._next:
            return self._next.optimize(commands)
        return commands

from domain.gcode_optimizer import GCodeOptimizer

class ColinearOptimizer(GCodeOptimizer):
    """Optimiza secuencias de MoveCommand colineales (antes estaba en el builder)."""
    def optimize(self, commands):
        from domain.gcode.commands.move_command import MoveCommand
        optimized_cmds = []
        i = 0
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
                        if dx * dy_prev != dy * dx_prev:
                            optimized_points.append(points[k-1])
                            dx_prev = dx
                            dy_prev = dy
                    optimized_points.append(points[-1])
                    for idx, (x, y) in enumerate(optimized_points):
                        optimized_cmds.append(MoveCommand(x, y, feed if idx == 0 else None, rapid=False))
                else:
                    for k in range(start, j):
                        optimized_cmds.append(commands[k])
                i = j
            else:
                optimized_cmds.append(cmd)
                i += 1
        return self._call_next(optimized_cmds)

from domain.gcode.commands.arc_command import ArcCommand
from domain.gcode_optimizer import GCodeOptimizer
from domain.gcode.commands.move_command import MoveCommand
from typing import List
import math

class ArcOptimizer(GCodeOptimizer):
    """Detecta secuencias de movimientos que pueden representarse como arcos y las reemplaza por ArcCommand."""
    def __init__(self, tolerance=0.1, min_points=3):
        super().__init__()
        self.tolerance = tolerance
        self.min_points = min_points

    def optimize(self, commands: List[BaseCommand]) -> List[BaseCommand]:
        result = []
        i = 0
        while i < len(commands):
            # Detectar secuencia de MoveCommand elegible
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
                    arc = self._fit_arc(arc_seq)
                    if arc:
                        result.append(arc)
                        i = j
                        continue
                # Si no se detecta arco, agregar los comandos tal cual
                result.extend(arc_seq)
                i = j
            else:
                result.append(commands[i])
                i += 1
        return self._call_next(result)

    def _fit_arc(self, moves: List[MoveCommand]):
        # Algoritmo simple: solo detecta arcos perfectos de 3 puntos
        if len(moves) != 3:
            return None
        p1, p2, p3 = moves[0], moves[1], moves[2]
        # Calcular el centro y radio del círculo que pasa por los 3 puntos
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        temp = x2**2 + y2**2
        bc = (x1**2 + y1**2 - temp) / 2.0
        cd = (temp - x3**2 - y3**2) / 2.0
        det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)
        if abs(det) < 1e-6:
            return None  # Puntos colineales
        cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
        cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
        r = math.hypot(x1 - cx, y1 - cy)
        # Verificar que todos los puntos estén a distancia ~r del centro
        for p in [p1, p2, p3]:
            if abs(math.hypot(p.x - cx, p.y - cy) - r) > self.tolerance:
                return None
        # Calcular parámetros I, J (vector desde inicio al centro)
        i = cx - x1
        j = cy - y1
        # Determinar sentido (horario/antihorario) usando determinante
        clockwise = ((x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)) < 0
        return ArcCommand(x3, y3, i, j, clockwise, feed=p1.feed)
