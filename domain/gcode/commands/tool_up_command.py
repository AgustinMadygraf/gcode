"""
ToolUpCommand: Comando para levantar herramienta (ejecutar CMD_UP).
"""
from domain.gcode.commands.base_command import BaseCommand

class ToolUpCommand(BaseCommand):
    def __init__(self, cmd_up: str):
        self.cmd_up = cmd_up
    def to_gcode(self) -> str:
        return self.cmd_up
