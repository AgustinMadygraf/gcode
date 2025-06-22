"""
ArcCommand: Comando G2/G3 para movimientos de arco en G-code.
RelativeMoveCommand: Comando G91 para movimientos relativos.
"""
from domain.gcode.commands.base_command import BaseCommand

class ArcCommand(BaseCommand):
    def __init__(self, x: float, y: float, i: float, j: float, clockwise: bool = True, feed: float = None):
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.clockwise = clockwise
        self.feed = feed

    def to_gcode(self) -> str:
        cmd = "G2" if self.clockwise else "G3"
        feed_str = f" F{self.feed}" if self.feed is not None else ""
        return f"{cmd} X{self.x:.3f} Y{self.y:.3f} I{self.i:.3f} J{self.j:.3f}{feed_str}"

class RelativeMoveCommand(BaseCommand):
    def __init__(self, x: float, y: float, feed: float = None, rapid: bool = False):
        self.x = x
        self.y = y
        self.feed = feed
        self.rapid = rapid

    def to_gcode(self) -> str:
        cmd = "G0" if self.rapid else "G1"
        feed_str = f" F{self.feed}" if self.feed is not None else ""
        return f"G91\n{cmd} X{self.x:.3f} Y{self.y:.3f}{feed_str}\nG90"  # G91 activa modo relativo, G90 vuelve a absoluto
