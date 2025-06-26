"""
Mocks para pruebas relacionadas con configuración y settings.
"""

class DummyLogger:
    """
    Implementación simulada de un logger para tests.
    Registra mensajes en la salida estándar.
    """
    def info(self, msg):
        """Registra un mensaje informativo."""
        pass
    
    def debug(self, msg):
        """Registra un mensaje de depuración."""
        pass
    
    def error(self, msg):
        """Registra un mensaje de error."""
        pass

class DummyConfig:
    """
    Implementación simulada de objeto de configuración para tests.
    Proporciona valores predeterminados para pruebas.
    """
    max_height_mm = 250.0
    
    def __init__(self, temp_dir):
        self._temp_dir = temp_dir
    
    def get_gcode_output_dir(self):
        """Devuelve el directorio configurado para salida de archivos G-code"""
        from pathlib import Path
        return Path(self._temp_dir)

class DummyConfigProvider:
    """
    Implementación simulada de un proveedor de configuración para tests.
    """
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
    
    def get_gcode_output_dir(self):
        """Devuelve el directorio configurado para salida de archivos G-code"""
        from pathlib import Path
        return Path(self.temp_dir)
