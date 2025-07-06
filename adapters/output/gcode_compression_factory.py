"""
GcodeCompressionFactory: Permite seleccionar la estrategia de compresión de G-code según configuración.
"""
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service

class GcodeCompressionFactory:
    " Factory para crear el servicio de compresión de G-code según configuración. "
    @staticmethod
    def get_compression_service(config, logger=None):
        " Devuelve un servicio de compresión de G-code según la configuración. "
        if hasattr(config, 'disable_gcode_compression') and config.disable_gcode_compression:
            return None
        i18n = getattr(config, 'i18n', None)
        return create_gcode_compression_service(logger=logger, i18n=i18n)
