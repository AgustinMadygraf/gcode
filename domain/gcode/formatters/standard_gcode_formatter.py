"""
StandardGCodeFormatter: Formatea comandos G-code en el formato estándar actual.
"""
from domain.gcode.formatters.base_formatter import BaseFormatter
from domain.gcode.commands.base_command import BaseCommand

class StandardGCodeFormatter(BaseFormatter):
    def format_command(self, command: BaseCommand) -> str:
        return command.to_gcode()
