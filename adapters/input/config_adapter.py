"""
Path: adapters/input/config_adapter.py
Adaptador para leer configuración desde config.json
"""

from domain.ports.config_port import ConfigPort
from domain.compression_config import CompressionConfig

class ConfigAdapter(ConfigPort):
    """Adaptador para leer configuración desde config.json"""
    @property
    def flip_vertical(self):
        "Devuelve si se debe aplicar el flip vertical (FLIP_VERTICAL)."
        return getattr(self.config, 'flip_vertical', False)

    def get_flip_vertical(self):
        "Devuelve si se debe aplicar el flip vertical."
        return self.flip_vertical
    @property
    def rotate_90_clockwise(self):
        " Devuelve si debe rotar 90 grados en sentido horario (ROTATE_90_CLOCKWISE). "
        return getattr(self.config, 'rotate_90_clockwise', False)

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

    @property
    def marker_feed_rate(self):
        " Devuelve la tasa de avance del marcador (marker_feed_rate). "
        return self.config.marker_feed_rate

    @property
    def tool_type(self):
        " Devuelve el tipo de herramienta (tool_type). "
        return self.config.tool_type

    @property
    def pen_double_pass(self):
        " Devuelve si se debe hacer un doble pase con el marcador (pen_double_pass). "
        return self.config.pen_double_pass

    def get(self, key, default=None):
        " Devuelve el valor de la clave, o un valor por defecto si no existe. "
        return getattr(self.config, key, default)

    def get_debug_flag(self, name: str) -> bool:
        """Devuelve el flag de debug para un componente dado."""
        return self.config.get_debug_flag(name)
