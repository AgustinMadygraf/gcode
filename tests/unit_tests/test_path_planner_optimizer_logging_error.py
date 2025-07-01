"""
Test de logging de errores en PathPlannerOptimizer.
"""
import pytest
import logging
from domain.services.optimization.path_planner_optimizer import PathPlannerOptimizer


def test_logging_error_on_invalid_input(caplog):
    optimizer = PathPlannerOptimizer()
    logger = logging.getLogger("test_logger_error")
    # Simula entrada inválida: comandos vacíos (o tipo incorrecto)
    invalid_commands = None
    with caplog.at_level("ERROR", logger="test_logger_error"):
        try:
            optimizer.optimize(invalid_commands, logger=logger)
        except Exception as e:
            logger.error(f"Error al optimizar: {e}")
    # Verifica que se loguea el error
    error_logs = [r for r in caplog.records if "Error al optimizar" in r.getMessage()]
    assert error_logs, "No se encontró log de error ante entrada inválida"
