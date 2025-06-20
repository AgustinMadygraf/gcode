"""
DwellCommand: Comando para pausas G4.
"""
from domain.gcode.commands.base_command import BaseCommand

class DwellCommand(BaseCommand):
    def __init__(self, dwell_seconds: float):
        self.dwell_seconds = dwell_seconds
    def to_gcode(self) -> str:
        return f"G4 P{self.dwell_seconds:.3f}"
