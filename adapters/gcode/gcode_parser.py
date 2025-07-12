"""
G-code parser and serializer for offset correction workflow.
"""
from typing import List

# Dummy G-code command class for demonstration
class GCodeCommand:
    def __init__(self, line: str):
        self.line = line
    def apply_offset(self, offset_x: float, offset_y: float):
        # Implement offset logic for real G-code commands here
        pass
    def __str__(self):
        return self.line


def parse_gcode_lines(lines: List[str]) -> List[GCodeCommand]:
    """Parse G-code lines into command objects."""
    return [GCodeCommand(line.strip()) for line in lines if line.strip()]


def serialize_gcode_commands(commands: List[GCodeCommand]) -> List[str]:
    """Serialize command objects back to G-code lines."""
    return [str(cmd) for cmd in commands]
