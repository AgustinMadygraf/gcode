"""
Tests de logging para PathPlannerOptimizer usando caplog.
"""

import pytest
import logging
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

def test_logging_info_emitted_on_optimize(make_trazo, caplog):
    trazo1 = make_trazo([(0,0), (10,0)])
    trazo2 = make_trazo([(50,50), (52,50)])
    trazo3 = make_trazo([(10,0), (15,0)])
    inicio = [MoveCommand(0, 0, rapid=True)]
    commands = inicio + trazo2 + trazo3 + trazo1
    optimizer = PathPlannerOptimizer()
    logger = logging.getLogger("test_logger")
    with caplog.at_level("INFO", logger="test_logger"):
        optimized, metrics = optimizer.optimize(commands, logger=logger)
    # Verifica que se loguea el orden de trazos
    orden_logs = [r for r in caplog.records if "Orden final de trazos" in r.getMessage()]
    assert orden_logs, "No se encontró log de orden de trazos"
    # Verifica que se loguean las métricas
    metric_logs = [r for r in caplog.records if "Métricas de optimización" in r.getMessage()]
    assert metric_logs, "No se encontró log de métricas de optimización"
    # Verifica nivel
    for r in orden_logs + metric_logs:
        assert r.levelname == "INFO"

def test_logging_no_logger_does_not_fail(make_trazo):
    trazo1 = make_trazo([(0,0), (10,0)])
    trazo2 = make_trazo([(50,50), (52,50)])
    inicio = [MoveCommand(0, 0, rapid=True)]
    commands = inicio + trazo2 + trazo1
    optimizer = PathPlannerOptimizer()
    # No debe lanzar excepción si logger es None
    optimized, metrics = optimizer.optimize(commands, logger=None)
    assert isinstance(optimized, list)
    assert isinstance(metrics, dict)
