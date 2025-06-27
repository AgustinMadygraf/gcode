"""
GcodeGenerationConfigHelper: encapsula la obtención de flags de configuración para la generación de G-code.
"""
class GcodeGenerationConfigHelper:
    @staticmethod
    def get_remove_border(config):
        try:
            return config.get("REMOVE_BORDER_RECTANGLE", True)
        except Exception:
            return True

    @staticmethod
    def get_use_relative_moves(config):
        try:
            if hasattr(config, '_data') and "COMPRESSION" in config._data:
                return config._data["COMPRESSION"].get("USE_RELATIVE_MOVES", False)
            else:
                return config.get("USE_RELATIVE_MOVES", False)
        except Exception:
            return False
