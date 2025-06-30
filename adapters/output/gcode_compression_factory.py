"""
GcodeCompressionFactory: Permite seleccionar la estrategia de compresión de G-code según configuración.
"""
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service

class GcodeCompressionFactory:
    @staticmethod
    def get_compression_service(config, logger=None):
        # Permite desactivar la compresión si config tiene el flag correspondiente
        if hasattr(config, 'disable_gcode_compression') and config.disable_gcode_compression:
            return None
        return create_gcode_compression_service(logger=logger)
