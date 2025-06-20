"""
GCodeCommandBuilder: Permite construir secuencias de comandos G-code de forma fluida.
"""
from typing import List
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.tool_up_command import ToolUpCommand
from domain.gcode.commands.tool_down_command import ToolDownCommand
from domain.gcode.commands.move_command import MoveCommand
from domain.gcode.commands.dwell_command import DwellCommand

class GCodeCommandBuilder:
    def __init__(self):
        self.commands: List[BaseCommand] = []

    def tool_up(self, cmd_up: str):
        self.commands.append(ToolUpCommand(cmd_up))
        return self

    def tool_down(self, cmd_down: str):
        self.commands.append(ToolDownCommand(cmd_down))
        return self

    def move_to(self, x: float, y: float, feed: float = None, rapid: bool = False):
        self.commands.append(MoveCommand(x, y, feed, rapid))
        return self

    def dwell(self, seconds: float):
        self.commands.append(DwellCommand(seconds))
        return self

    def build(self) -> List[BaseCommand]:
        return self.commands

    def to_gcode_lines(self) -> List[str]:
        # Optimización: fusionar movimientos G1 colineales consecutivos
        optimized_cmds = []
        i = 0
        while i < len(self.commands):
            cmd = self.commands[i]
            # Solo optimizamos secuencias de MoveCommand (G1, no rapid)
            if (
                isinstance(cmd, MoveCommand)
                and not cmd.rapid
                and i + 1 < len(self.commands)
            ):
                # Iniciar secuencia
                start = i
                points = [(cmd.x, cmd.y)]
                feed = cmd.feed
                # Buscar secuencia colineal
                j = i + 1
                while (
                    j < len(self.commands)
                    and isinstance(self.commands[j], MoveCommand)
                    and not self.commands[j].rapid
                ):
                    points.append((self.commands[j].x, self.commands[j].y))
                    j += 1
                # Si hay al menos 3 puntos, buscar colinealidad
                if len(points) >= 3:
                    optimized_points = [points[0]]
                    dx_prev = points[1][0] - points[0][0]
                    dy_prev = points[1][1] - points[0][1]
                    for k in range(2, len(points)):
                        dx = points[k][0] - points[k-1][0]
                        dy = points[k][1] - points[k-1][1]
                        # Si la dirección cambia, guardar el anterior
                        if dx * dy_prev != dy * dx_prev:
                            optimized_points.append(points[k-1])
                            dx_prev = dx
                            dy_prev = dy
                    optimized_points.append(points[-1])
                    # Agregar comandos optimizados
                    for idx, (x, y) in enumerate(optimized_points):
                        optimized_cmds.append(MoveCommand(x, y, feed if idx == 0 else None, rapid=False))
                else:
                    # Menos de 3 puntos, no optimizar
                    for k in range(start, j):
                        optimized_cmds.append(self.commands[k])
                i = j
            else:
                optimized_cmds.append(cmd)
                i += 1
        return [cmd.to_gcode() for cmd in optimized_cmds]
