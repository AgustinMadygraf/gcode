"""
Path: infrastructure/performance/timing.py

"""

import time
import functools
import contextlib
from typing import Callable

class PerformanceTimer:
    " Utilidad para medir y loguear tiempos de ejecución en modo desarrollador. "
    DEBUG_ENABLED = False
    
    @classmethod
    def _debug(cls, logger, msg):
        if cls.DEBUG_ENABLED and logger:
            logger.debug(msg)

    @staticmethod
    @contextlib.contextmanager
    def measure(logger, operation_name: str, level: str = "DEBUG", skip_if_not_dev: bool = True):
        """Context manager para medir bloques de código.
        Args:
            logger: Logger a utilizar
            operation_name: Nombre de la operación
            level: Nivel de log (DEBUG/INFO)
            skip_if_not_dev: Solo mide si está activo el modo dev
        """
        dev_mode = getattr(logger, 'show_file_line', False) or getattr(logger, 'dev_mode', False)
        if not dev_mode and skip_if_not_dev and not PerformanceTimer.DEBUG_ENABLED:
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            msg = f"⏱️ Timing: {operation_name} completed in {elapsed:.3f}s"
            if PerformanceTimer.DEBUG_ENABLED:
                PerformanceTimer._debug(logger, msg)
            elif level.upper() == "DEBUG":
                logger.debug(msg)
                print("\n")
            elif level.upper() == "INFO":
                logger.info(msg)

    @staticmethod
    def timed_method(level: str = "DEBUG", skip_input: bool = True, skip_if_not_dev: bool = True):
        """Decorador para medir métodos.
        Args:
            level: Nivel de log
            skip_input: Excluye funciones de input
            skip_if_not_dev: Solo mide si está activo el modo dev
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if skip_input and ("input" in func.__name__.lower()):
                    return func(self, *args, **kwargs)
                logger = getattr(self, 'logger', None) or kwargs.get('logger', None)
                dev_mode = getattr(logger, 'show_file_line', False) or getattr(logger, 'dev_mode', False)
                if not logger or (not dev_mode and skip_if_not_dev and not PerformanceTimer.DEBUG_ENABLED):
                    return func(self, *args, **kwargs)
                name = f"{self.__class__.__name__}.{func.__name__}"
                start = time.perf_counter()
                result = func(self, *args, **kwargs)
                elapsed = time.perf_counter() - start
                msg = f"⏱️ Timing: {name} completed in {elapsed:.3f}s"
                if PerformanceTimer.DEBUG_ENABLED:
                    PerformanceTimer._debug(logger, msg)
                elif level.upper() == "DEBUG":
                    logger.debug(msg)
                elif level.upper() == "INFO":
                    logger.info(msg)
                return result
            return wrapper
        return decorator
