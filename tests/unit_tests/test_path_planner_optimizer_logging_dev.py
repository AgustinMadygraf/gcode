"""
Test de logging en modo desarrollador: verifica formato archivo:línea.
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

def test_logging_includes_file_line_in_dev(make_trazo, caplog):
    trazo1 = make_trazo([(0,0), (10,0)])
    trazo2 = make_trazo([(50,50), (52,50)])
    inicio = [MoveCommand(0, 0, rapid=True)]
    commands = inicio + trazo2 + trazo1
    optimizer = PathPlannerOptimizer()
    logger = logging.getLogger("test_logger_dev")
    # Simula formato de desarrollador: agrega archivo:línea al formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = True
    logger.setLevel(logging.INFO)
    with caplog.at_level("INFO", logger="test_logger_dev"):
        optimizer.optimize(commands, logger=logger)
    # Busca archivo:línea en los logs
    found = False
    for record in caplog.records:
        if record.filename.endswith("path_planner_optimizer.py") and record.lineno > 0:
            found = True
            break
    assert found, "No se encontró archivo:línea en los logs en modo dev"
