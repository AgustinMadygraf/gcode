"""
Mocks para pruebas de generación de GCode.
"""
from domain.ports.gcode_generator_port import GcodeGeneratorPort

class MockGCodeGenerator(GcodeGeneratorPort):
    """
    Implementación simulada del generador GCode para pruebas unitarias.
    """
    def __init__(self, **kwargs):
        pass
        
    def generate(self, paths, svg_attr):
        """Simula G-code con comandos CMD_DOWN y CMD_UP"""
        return ["G1 X0 Y0", "M3 S255", "G1 X1 Y1", "M5"]
