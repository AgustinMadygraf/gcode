"""
Path: infrastructure/performance/timing.py

Utilidad para medir y loguear tiempos de ejecución en modo desarrollador.
El debug se controla mediante el flag 'PerformanceTimer' en la configuración.
"""

import time
import functools
import contextlib
from typing import Callable

class PerformanceTimer:
    """
    Utilidad para medir y loguear tiempos de ejecución en modo desarrollador.
    El debug se controla mediante el flag 'PerformanceTimer' en la configuración.
    """
    def __init__(self, container, config=None):
        self.container = container
        self.logger = getattr(container, 'logger', None)
        self.config = config or getattr(container, 'config', None)

    def _debug(self, msg, *args, **kwargs):
        """
        Muestra mensajes de debug solo si el flag 'PerformanceTimer' está activado en la configuración.
        """
        debug_enabled = False
        if self.config and hasattr(self.config, "get_debug_flag"):
            debug_enabled = self.config.get_debug_flag("PerformanceTimer")
        if debug_enabled and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    @contextlib.contextmanager
    def measure(self, operation_name: str, level: str = "DEBUG", skip_if_not_dev: bool = True):
        """
        Context manager para medir bloques de código.
        Args:
            operation_name: Nombre de la operación
            level: Nivel de log (DEBUG/INFO)
            skip_if_not_dev: Solo mide si está activo el modo dev o debug
        """
        dev_mode = getattr(self.logger, 'show_file_line', False) or getattr(self.logger, 'dev_mode', False)
        debug_enabled = False
        if self.config and hasattr(self.config, "get_debug_flag"):
            debug_enabled = self.config.get_debug_flag("PerformanceTimer")
        if not dev_mode and skip_if_not_dev and not debug_enabled:
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            msg = f"⏱️ Timing: {operation_name} completed in {elapsed:.3f}s"
            if debug_enabled:
                self._debug(msg)
            elif level.upper() == "DEBUG":
                if self.logger:
                    self.logger.debug(msg)
                print("\n")
            elif level.upper() == "INFO":
                if self.logger:
                    self.logger.info(msg)

    def timed_method(self, level: str = "DEBUG", skip_input: bool = True, skip_if_not_dev: bool = True):
        """
        Decorador para medir métodos.
        Args:
            level: Nivel de log
            skip_input: Excluye funciones de input
            skip_if_not_dev: Solo mide si está activo el modo dev o debug
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(self_, *args, **kwargs):
                if skip_input and ("input" in func.__name__.lower()):
                    return func(self_, *args, **kwargs)
                logger = getattr(self_, 'logger', None) or kwargs.get('logger', None)
                config = getattr(self_, 'config', None)
                dev_mode = getattr(logger, 'show_file_line', False) or getattr(logger, 'dev_mode', False)
                debug_enabled = False
                if config and hasattr(config, "get_debug_flag"):
                    debug_enabled = config.get_debug_flag("PerformanceTimer")
                if not logger or (not dev_mode and skip_if_not_dev and not debug_enabled):
                    return func(self_, *args, **kwargs)
                name = f"{self_.__class__.__name__}.{func.__name__}"
                start = time.perf_counter()
                result = func(self_, *args, **kwargs)
                elapsed = time.perf_counter() - start
                msg = f"⏱️ Timing: {name} completed in {elapsed:.3f}s"
                if debug_enabled:
                    if hasattr(self_, "_debug"):
                        self_._debug(msg)
                    elif logger:
                        logger.debug(msg)
                elif level.upper() == "DEBUG":
                    logger.debug(msg)
                elif level.upper() == "INFO":
                    logger.info(msg)
                return result
            return wrapper
        return decorator
