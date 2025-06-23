from domain.ports.config_port import ConfigPort
from domain.models.compression_config import CompressionConfig

class ConfigImpl(ConfigPort):
    """Adaptador para leer configuración desde config.json"""

    def __init__(self, config):
        self.config = config

    def get_compression_config(self) -> CompressionConfig:
        compression_data = self.config.get("COMPRESSION", {})
        return CompressionConfig(
            enabled=compression_data.get("ENABLED", True),
            geometric_tolerance=compression_data.get("GEOMETRIC_TOLERANCE", 0.1),
            use_arcs=compression_data.get("USE_ARCS", True),
            use_relative_moves=compression_data.get("USE_RELATIVE_MOVES", False),
            remove_redundancies=compression_data.get("REMOVE_REDUNDANCIES", True)
        )
