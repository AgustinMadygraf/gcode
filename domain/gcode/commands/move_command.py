"""
MoveCommand: Comando para movimientos G0/G1.
"""
from domain.gcode.commands.base_command import BaseCommand

class MoveCommand(BaseCommand):
    def __init__(self, x: float, y: float, feed: float = None, rapid: bool = False):
        self.x = x
        self.y = y
        self.feed = feed
        self.rapid = rapid
    def to_gcode(self) -> str:
        cmd = "G0" if self.rapid else "G1"
        line = f"{cmd} X{self.x:.3f} Y{self.y:.3f}"
        if self.feed is not None and not self.rapid:
            line += f" F{self.feed}"
        return line
