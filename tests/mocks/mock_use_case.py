"""
Mocks para pruebas de casos de uso.
"""
from pathlib import Path

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
    def process(self, paths, attrs):
        return paths[:2]  # Simula filtrado

class DummyGcodeGen:
    """Mock de generador de GCode para casos de uso"""
    def generate(self, paths, attrs, context=None):
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
    def info(self, *a, **k): 
        pass
    
    def error(self, *a, **k):
        pass
    
    def debug(self, *a, **k):
        pass

class DummyFilenameService:
    """Mock de servicio de nombres de archivo"""
    pass
