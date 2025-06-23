# Caso de uso: compresión de G-code
# Orquesta la compresión usando GcodeCompressionService y retorna métricas

class CompressGcodeUseCase:
    def __init__(self, compression_service, config_reader):
        self.compression_service = compression_service
        self.config_reader = config_reader

    def execute(self, gcode_data):
        # Leer configuración de compresión
        config = self.config_reader.get_compression_config()
        # Ejecutar compresión
        compressed, metrics = self.compression_service.compress(gcode_data, config)
        # Retornar métricas y gcode comprimido
        return {
            'original_size': metrics.original_lines,
            'compressed_size': metrics.compressed_lines,
            'compression_ratio': metrics.compressed_lines / metrics.original_lines if metrics.original_lines else 0,
            'compressed_gcode': compressed
        }
