"""
Mocks para pruebas de casos de uso.
"""

class DummyLoader:
    """Mock de cargador para casos de uso"""
    def __init__(self, svg_file):
        self.svg_file = svg_file
        
    def get_paths(self):
        return [1, 2, 3]  # Simula paths
        
    def get_attributes(self):
        return {'width': 100, 'height': 100}

class DummyPathProcessor:
    """Mock de procesador de rutas"""
    def process(self, paths, _attrs, context=None): # pylint: disable=unused-argument
        return paths[:2]  # Simula filtrado

class DummyGcodeGen:
    """Mock de generador de GCode para casos de uso"""
    def generate(self, paths, _attrs, _context=None, **_kwargs):
        return [f'G1 X{p}' for p in paths]

class DummyCompressUseCase:
    """Mock de caso de uso de compresión"""
    def execute(self, gcode_lines):
        return {
            'compressed_gcode': gcode_lines[::-1], 
            'original_size': len(gcode_lines), 
            'compressed_size': len(gcode_lines), 
            'compression_ratio': 1.0
        }

class DummyLogger:
    """Mock de logger"""
    def info(self, *_a, **_k): 
        pass
    def error(self, *_a, **_k):
        pass
    def debug(self, *_a, **_k):
        pass
    def warning(self, *_a, **_k):
        pass

class DummyFilenameService:
    """Mock de servicio de nombres de archivo"""
    pass  # pylint: disable=unnecessary-pass
