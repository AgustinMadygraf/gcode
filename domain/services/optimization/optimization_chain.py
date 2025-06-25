from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.services.optimization.arc_optimizer import ArcOptimizer
from domain.services.optimization.colinear_optimizer import ColinearOptimizer
from domain.services.optimization.line_optimizer import LineOptimizer
from domain.services.optimization.path_planner_optimizer import PathPlannerOptimizer

class OptimizationChain(GcodeOptimizationChainPort):
    def __init__(self, optimizers=None):
        self.optimizers = optimizers or [
            PathPlannerOptimizer(min_distance=5.0),  # Primero reordenar los trazos
            LineOptimizer(tolerance=0.001),  # Luego consolidar líneas
            ColinearOptimizer(),
            ArcOptimizer(tolerance=0.1)
        ]

    def optimize(self, commands):
        current_commands = commands
        metrics = {}
        for optimizer in self.optimizers:
            current_commands, opt_metrics = optimizer.optimize(current_commands)
            metrics.update(opt_metrics)
        return current_commands, metrics
