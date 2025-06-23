from infrastructure.optimizers.arc_optimizer import ArcOptimizer
from infrastructure.optimizers.colinear_optimizer import ColinearOptimizer
from infrastructure.optimizers.optimization_chain import OptimizationChain

def make_optimization_chain():
    return OptimizationChain([ArcOptimizer(tolerance=0.1), ColinearOptimizer()])
