"""
ToolDownCommand: Comando para bajar herramienta (ejecutar CMD_DOWN).
"""
from domain.gcode.commands.base_command import BaseCommand

class ToolDownCommand(BaseCommand):
    def __init__(self, cmd_down: str):
        self.cmd_down = cmd_down
    def to_gcode(self) -> str:
        return self.cmd_down
