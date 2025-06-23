from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from infrastructure.optimizers.arc_optimizer import ArcOptimizer
from infrastructure.optimizers.colinear_optimizer import ColinearOptimizer

# Este archivo fue movido a domain/services/optimization/optimization_chain.py

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
