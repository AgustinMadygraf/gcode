from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.services.optimization.arc_optimizer import ArcOptimizer
from domain.services.optimization.colinear_optimizer import ColinearOptimizer

class OptimizationChain(GcodeOptimizationChainPort):
    def __init__(self, optimizers=None):
        self.optimizers = optimizers or [ArcOptimizer(tolerance=0.1), ColinearOptimizer()]

    def optimize(self, commands):
        current_commands = commands
        metrics = {}
        for optimizer in self.optimizers:
            current_commands, opt_metrics = optimizer.optimize(current_commands)
            metrics.update(opt_metrics)
        return current_commands, metrics
