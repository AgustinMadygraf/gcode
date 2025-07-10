"""
Path: infrastructure/logger_helper.py
This module provides a helper class for logging debug messages.
"""

class LoggerHelper:
    """Helper class for logging debug messages."""

    def __init__(self, config=None, logger=None):
        self.config = config
        self.logger = logger
        
    def _get_debug_class_name(self):
        """
        Returns the class name to use for the debug flag.
        Override this in subclasses if needed.
        """
        return self.__class__.__name__
        
    def _debug(self, msg, *args, **kwargs):
        debug_enabled = False
        if hasattr(self, "config") and self.config and hasattr(self.config, "get_debug_flag"):
            debug_enabled = self.config.get_debug_flag(self._get_debug_class_name())
        else:
            debug_enabled = False
        if debug_enabled and hasattr(self, "logger") and self.logger:
            # stacklevel=3 para que apunte al llamador real
            self.logger.debug(msg, *args, stacklevel=3, **kwargs)
