"""
Mocks para pruebas relacionadas con configuración y settings.
"""

class DummyConfigProvider:
    """
    Implementación simulada de un proveedor de configuración para tests.
    """
    def __init__(self, output_dir):
        self._output_dir = output_dir
    
    def get_gcode_output_dir(self):
        """Devuelve el directorio configurado para salida de archivos G-code"""
        return self._output_dir

class DummyConfig:
    """
    Implementación simulada de objeto de configuración para tests.
    Proporciona valores predeterminados para pruebas.
    """
    def __init__(self, values=None):
        self.values = values or {}
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración por su clave"""
        return self.values.get(key, default)
    
    def __getattr__(self, name):
        """Permite acceso a configuración como atributo"""
        return self.values.get(name)
