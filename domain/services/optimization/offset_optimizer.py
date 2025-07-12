from typing import List, Dict, Any, Tuple
from domain.ports.gcode_optimization_port import GcodeOptimizationPort

class OffsetOptimizer(GcodeOptimizationPort):
    """
    Shift entire G-CODE program along X/Y axes.
    Applies absolute or relative offset to movement commands.
    """
    def __init__(self, offset_x: float = 0.0, offset_y: float = 0.0, is_relative: bool = False):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.is_relative = is_relative

    def optimize(self, commands: List[Any], tolerance: float = 0.0) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Applies X/Y offset to all movement commands (MoveCommand, ArcCommand, etc).
        Returns new command list and metrics.
        """
        offset_applied = 0
        new_commands = []
        for cmd in commands:
            # Only apply to commands with x/y attributes (e.g. MoveCommand, ArcCommand)
            if hasattr(cmd, 'x') and hasattr(cmd, 'y'):
                orig_x, orig_y = cmd.x, cmd.y
                if self.is_relative:
                    cmd.x = orig_x * (1 + self.offset_x)
                    cmd.y = orig_y * (1 + self.offset_y)
                else:
                    cmd.x = orig_x + self.offset_x
                    cmd.y = orig_y + self.offset_y
                offset_applied += 1
            new_commands.append(cmd)
        metrics = {
            "offset_applied": offset_applied,
            "total_commands": len(commands),
            "optimization_rate": offset_applied / len(commands) if commands else 0.0
        }
        return new_commands, metrics
