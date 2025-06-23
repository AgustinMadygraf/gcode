"""
GCodeCommandBuilder: Permite construir secuencias de comandos G-code de forma fluida.
"""
from typing import List
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.tool_up_command import ToolUpCommand
from domain.gcode.commands.tool_down_command import ToolDownCommand
from domain.gcode.commands.move_command import MoveCommand
from domain.gcode.commands.dwell_command import DwellCommand
from domain.gcode_optimizer import GCodeOptimizer

class GCodeCommandBuilder:
    def __init__(self, optimizer: GCodeOptimizer = None):
        self.commands: List[BaseCommand] = []
        self.optimizer = optimizer

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
        cmds = self.commands
        if self.optimizer:
            cmds = self.optimizer.optimize(cmds)
        return [cmd.to_gcode() for cmd in cmds]

    def to_gcode_lines_with_metrics(self):
        cmds = self.commands
        metrics = {}
        if self.optimizer:
            # Si el optimizador devuelve (cmds, metrics)
            result = self.optimizer(cmds)
            if isinstance(result, tuple) and len(result) == 2:
                cmds, metrics = result
            else:
                cmds = result
        return [cmd.to_gcode() for cmd in cmds], metrics
