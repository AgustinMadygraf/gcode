from domain.ports.gcode_optimization_factory_port import GcodeOptimizationFactoryPort
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from application.use_cases.gcode_generation.optimization_chain import OptimizationChain
from infrastructure.optimizers.arc_optimizer import ArcOptimizer
from infrastructure.optimizers.colinear_optimizer import ColinearOptimizer

class GcodeOptimizationFactory(GcodeOptimizationFactoryPort):
    def create_optimization_chain(self) -> GcodeOptimizationChainPort:
        chain = OptimizationChain()
        chain.add_optimizer(ArcOptimizer())
        chain.add_optimizer(ColinearOptimizer())
        return chain
