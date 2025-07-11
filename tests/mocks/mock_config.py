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
        pass # noqa: W0107  # pylint: disable=unnecessary-pass
    
    def debug(self, msg):
        """Registra un mensaje de depuración."""
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

    def error(self, msg):
        """Registra un mensaje de error."""
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

class DummyConfig:
    """
    Implementación simulada de objeto de configuración para tests.
    Proporciona valores predeterminados para pruebas.
    """
    def __init__(self, temp_dir):
        self._temp_dir = temp_dir
    
    @property
    def plotter_max_area_mm(self):
        return [180.0, 250.0]
    
    def get_gcode_output_dir(self):
        """Devuelve el directorio configurado para salida de archivos G-code"""
        from pathlib import Path
        return Path(self._temp_dir)

    def get(self, key, default=None):
        """Simula la obtención de valores de configuración por clave."""
        if key == "TARGET_WRITE_AREA_MM":
            return [297.0, 210.0]
        if key == "PLOTTER_MAX_AREA_MM":
            return [300.0, 260.0]
        return default

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

def test_dummy_logger_methods():
    logger = DummyLogger()
    logger.info("info")
    logger.debug("debug")
    logger.error("error")
    # No hay assert porque solo se prueba que no falla

def test_dummy_config_properties(tmp_path):
    cfg = DummyConfig(str(tmp_path))
    assert cfg.plotter_max_area_mm == [180.0, 250.0]
    out_dir = cfg.get_gcode_output_dir()
    assert str(out_dir) == str(tmp_path)
    assert cfg.get("TARGET_WRITE_AREA_MM") == [297.0, 210.0]
    assert cfg.get("PLOTTER_MAX_AREA_MM") == [300.0, 260.0]
    assert cfg.get("NON_EXISTENT", 123) == 123

def test_dummy_config_provider(tmp_path):
    provider = DummyConfigProvider(str(tmp_path))
    out_dir = provider.get_gcode_output_dir()
    assert str(out_dir) == str(tmp_path)
