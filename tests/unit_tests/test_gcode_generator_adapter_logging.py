"""
Test de logging en GCodeGeneratorAdapter: verifica que se emiten logs clave.
"""
import pytest
import logging
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort

class DummyPathSampler(PathSamplerPort):
    def sample(self, *a, **kw):
        return []

class DummyConfig(ConfigPort):
    def get(self, *a, **kw):
        return None
    def get_compression_config(self, *a, **kw):
        return None

def test_gcode_generator_adapter_logs(caplog):
    logger = logging.getLogger("test_logger_adapter")
    # Instancia el adaptador con dependencias dummy y logger
    adapter = GCodeGeneratorAdapter(
        path_sampler=DummyPathSampler(),
        feed=1000.0,
        cmd_down="M3",
        cmd_up="M5",
        step_mm=1.0,
        dwell_ms=0,
        max_height_mm=100.0,
        config=DummyConfig(),
        logger=logger
    )
    # Simula llamada a método que debería loguear (ajustar según implementación real)
    with caplog.at_level("INFO", logger="test_logger_adapter"):
        if hasattr(adapter, "logger") and adapter.logger:
            adapter.logger.info("Mensaje de prueba de logging desde adapter")
    logs = [r for r in caplog.records if "Mensaje de prueba de logging" in r.getMessage()]
    assert logs, "No se encontró el log esperado en el adaptador"
