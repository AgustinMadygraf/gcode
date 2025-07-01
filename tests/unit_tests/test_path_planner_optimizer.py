"""
Test unitario para PathPlannerOptimizer: verifica el reordenamiento combinado por tamaño y cercanía.
"""
import pytest
from domain.services.optimization.path_planner_optimizer import PathPlannerOptimizer
from domain.gcode.commands.move_command import MoveCommand

@pytest.fixture
def make_trazo():
    def _make(points, feed=1000, rapid_first=True):
        cmds = []
        if rapid_first:
            cmds.append(MoveCommand(points[0][0], points[0][1], rapid=True))
        for x, y in points:
            cmds.append(MoveCommand(x, y, feed=feed, rapid=False))
        return cmds
    return _make

def test_reorder_strokes_by_length_and_proximity(make_trazo):
    # Trazo 1: largo (10 unidades)
    trazo1 = make_trazo([(0,0), (10,0)])
    # Trazo 2: corto (2 unidades), lejos
    trazo2 = make_trazo([(50,50), (52,50)])
    # Trazo 3: mediano (5 unidades), cerca del final de trazo1
    trazo3 = make_trazo([(10,0), (15,0)])
    # Comandos iniciales (inicio)
    inicio = [MoveCommand(0, 0, rapid=True)]
    # Mezclar el orden para probar el algoritmo
    commands = inicio + trazo2 + trazo3 + trazo1
    optimizer = PathPlannerOptimizer()
    optimized, metrics = optimizer.optimize(commands)
    # Extraer el orden de los trazos optimizados (por su primer punto, ignorando el bloque inicial)
    starts = [cmd for cmd in optimized if isinstance(cmd, MoveCommand) and cmd.rapid]
    # El primer grupo es el bloque inicial, los siguientes son los trazos reordenados
    # Verificamos el orden de los trazos reordenados
    reord_starts = [(s.x, s.y) for s in starts[1:]]
    assert reord_starts == [(0,0), (10,0), (50,50)] or reord_starts == [(10,0), (0,0), (50,50)]
    assert metrics["strategy"] == "length+proximity-dynamic"
