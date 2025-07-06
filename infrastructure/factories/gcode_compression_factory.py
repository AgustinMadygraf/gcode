"""
Path: infrastructure/factories/gcode_compression_factory.py
GcodeCompressionFactory: Permite crear un servicio de compresión de G-code con múltiples comp
"""


from domain.services.compression.line_compressor import LineCompressor
from infrastructure.compressors.arc_compressor import ArcCompressor
from application.use_cases.gcode_compression.gcode_compression_service import GcodeCompressionService

# Factory para crear el servicio de compresión con ambos compresores

def create_gcode_compression_service(logger=None, i18n=None):
    " Crea un servicio de compresión de G-code con múltiples compresores. "
    compressors = [
        ArcCompressor(),
        LineCompressor()
    ]
    return GcodeCompressionService(compressors, logger=logger, i18n=i18n)
